import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from skyfield.api import EarthSatellite, load, wgs84
from datetime import datetime, timedelta, timezone
from shapely.geometry import Polygon, Point # Tambah Point
from shapely.ops import unary_union
from pyproj import Geod
import csv, os
from sgp4.api import Satrec, jday

# Fungsi dari debris.py (copy untuk menghindari eksekusi kode debris.py)
def eci_to_latlon_local(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.degrees(np.arcsin(z / r))
    lon = np.degrees(np.arctan2(y, x))
    altitude = r - 6371.0  # Radius Bumi dalam km
    return lat, lon, altitude

def categorize_altitude_local(altitude):
    if 160 <= altitude < 528:
        return '160-528 km', 0
    elif 528 <= altitude < 896:
        return '528-896 km', 1
    elif 896 <= altitude < 1264:
        return '896-1264 km', 2
    elif 1264 <= altitude < 1632:
        return '1264-1632 km', 3
    elif 1632 <= altitude <= 2000:
        return '1632-2000 km', 4
    else:
        return 'Out of range', -1

def parse_debris_tle_local(tle_file_path, filter_category=None):
    """Parse debris TLE dengan filter kategori"""
    debris_positions = []
    
    with open(tle_file_path, 'r') as file:
        lines = file.readlines()
    
    current_time = datetime.utcnow()
    jd, fr = jday(current_time.year, current_time.month, current_time.day,
                  current_time.hour, current_time.minute, current_time.second)
    
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            line1 = lines[i + 1].strip()
            line2 = lines[i + 2].strip()
            
            try:
                debris = Satrec.twoline2rv(line1, line2)
                error, position, velocity = debris.sgp4(jd, fr)
                
                if error == 0:
                    x, y, z = position
                    lat, lon, alt = eci_to_latlon_local(x, y, z)
                    category, cat_idx = categorize_altitude_local(alt)
                    
                    # Filter berdasarkan kategori jika diminta
                    if filter_category is None or cat_idx == filter_category:
                        debris_positions.append({
                            'lat': lat,
                            'lon': lon,
                            'alt': alt,
                            'category': category,
                            'cat_idx': cat_idx
                        })
            except:
                continue
    
    return debris_positions

# ---------- TLE ISS (ZARYA) ----------
tle_lines = [
    "EXPLORER 22",
    "1 00899U 64064A   25276.49600160  .00000579  00000-0  49569-3 0  9991",
    "2 00899  79.6909  47.8810 0120383 146.1380 214.7533 13.82947257 69497"
]
# -------------------------------------

update_interval_ms = 200     # ms per frame
speedup = 127                # percepatan waktu simulasi
spotbeam_width_km = 2000     # lebar strip coverage tegak lurus lintasan (km)

# Inisialisasi skyfield
ts = load.timescale()
sat = EarthSatellite(tle_lines[1], tle_lines[2], tle_lines[0], ts)

# Geod untuk hitung area di ellipsoid WGS84
geod = Geod(ellps="WGS84")

# === Variabel CSV & Kontrol Penghentian ===
csv_filename = "spotbeam_data.csv"
save_counter = 0
max_saves = 5 # Batas maksimum baris CSV
stop_simulation = False # Variabel kontrol penghentian utama

# buat file baru jika belum ada
if not os.path.exists(csv_filename):
    with open(csv_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["UTC_time", "Latitude", "Longitude", "Altitude_km", "Spotbeam_Area_km2"])

def latlon_at_time(time_ts):
    geocentric = sat.at(time_ts)
    subpoint = wgs84.subpoint(geocentric)
    return subpoint.latitude.degrees, subpoint.longitude.degrees, subpoint.elevation.km

# === Deteksi kategori altitude satelit ===
print("\n[INFO] Mendeteksi altitude satelit...")
initial_time = ts.utc(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day,
                      datetime.utcnow().hour, datetime.utcnow().minute, datetime.utcnow().second)
initial_lat, initial_lon, initial_alt = latlon_at_time(initial_time)
sat_category, sat_cat_idx = categorize_altitude_local(initial_alt)

print(f"[INFO] Altitude satelit: {initial_alt:.2f} km")
print(f"[INFO] Kategori satelit: {sat_category}")

# === Load dan filter debris berdasarkan kategori satelit ===
print("[INFO] Memuat data debris...")
debris_filtered = parse_debris_tle_local('FENGYUN debris.txt', filter_category=sat_cat_idx if sat_cat_idx >= 0 else None)

print(f"[OK] Debris dalam kategori {sat_category}: {len(debris_filtered)} objek")

# Setup figure
fig = plt.figure(figsize=(14, 7))
ax = plt.axes(projection=ccrs.PlateCarree())

# Tambahkan fitur peta (style dari debris.py)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

# Plot debris yang sudah difilter
if len(debris_filtered) > 0:
    debris_lons = [d['lon'] for d in debris_filtered]
    debris_lats = [d['lat'] for d in debris_filtered]
    debris_alts = [d['alt'] for d in debris_filtered]
    
    debris_scatter = ax.scatter(debris_lons, debris_lats, c=debris_alts, s=15, alpha=0.6,
                               cmap='jet', transform=ccrs.PlateCarree(), 
                               label=f'Debris ({sat_category})', zorder=2)
    
    # Colorbar untuk debris altitude
    cbar = plt.colorbar(debris_scatter, ax=ax, orientation='horizontal',
                       pad=0.05, shrink=0.7)
    cbar.set_label(f'Debris Altitude (km) - Kategori: {sat_category}', fontsize=10)
    print(f"[OK] Debris berhasil diplot di peta")
else:
    print(f"[INFO] Tidak ada debris dalam kategori {sat_category}")

# Inisialisasi plot
line_artist, = ax.plot([], [], color='red', linewidth=2, label='Lintasan Satelit', transform=ccrs.Geodetic())
point_artist, = ax.plot([], [], 'bo', markersize=6, label='Satelit', transform=ccrs.Geodetic(), zorder=5)
spotbeam_artist, = ax.plot([], [], color='blue', alpha=0.3, transform=ccrs.Geodetic(), label="Spotbeam Strip")

time_text = ax.text(0.01, 0.03, '', transform=ax.transAxes, fontsize=9,
                    bbox=dict(facecolor='white', alpha=0.7))

area_text = ax.text(0.01, 0.08, '', transform=ax.transAxes, fontsize=9,
                    bbox=dict(facecolor='white', alpha=0.7))

# Title dengan info kategori
title_text = f'Animasi Satelit dengan Spotbeam Strip\nKategori: {sat_category} | Debris: {len(debris_filtered)} objek'
plt.title(title_text, fontsize=12, fontweight='bold')
plt.legend(loc='upper right', fontsize=9)

# Variabel penyimpan lintasan
track_lats = []
track_lons = []

# Variabel kontrol crossing orbit
start_real_time = datetime.utcnow().replace(tzinfo=timezone.utc)
start_sim_time = start_real_time
first_lat, first_lon = None, None # Titik awal simulasi
start_point = None # Titik awal sebagai objek Shapely
last_cross_state = False
cross_tolerance = 5.0

# Variabel untuk luas area cakupan
spotbeam_union = None
last_area_km2 = 0.0

def update(frame):
    global track_lats, track_lons, first_lat, first_lon, start_point, last_cross_state
    global spotbeam_union, last_area_km2, save_counter, stop_simulation

    # 🛑 MEKANISME PENGHENTIAN
    if stop_simulation:
        # Hentikan proses update frame jika kondisi penghentian terpenuhi
        return (point_artist, line_artist, spotbeam_artist, time_text, area_text)

    elapsed_real = frame * (update_interval_ms / 1000.0)
    sim_seconds = elapsed_real * speedup
    sim_time = start_sim_time + timedelta(seconds=sim_seconds)
    t_ts = ts.utc(sim_time.year, sim_time.month, sim_time.day,
                  sim_time.hour, sim_time.minute, sim_time.second + sim_time.microsecond/1e6)

    lat, lon, alt = latlon_at_time(t_ts)

    # Normalisasi longitude ke -180..180
    if lon > 180:
        lon -= 360
    elif lon < -180:
        lon += 360

    # Simpan dan definisikan titik awal hanya sekali
    if first_lat is None and first_lon is None:
        first_lat, first_lon = lat, lon
        start_point = Point(first_lon, first_lat) # Definisikan titik awal Shapely

    # ... (Logika deteksi crossing dan pembersihan lintasan tetap sama) ...
    dist = np.sqrt((lat - first_lat)**2 + (lon - first_lon)**2)
    is_crossing = dist < cross_tolerance
    if is_crossing and not last_cross_state:
        # Logika ini untuk membersihkan lintasan visual, bukan penghenti CSV utama lagi
        track_lats, track_lons = [], []
        # first_lat, first_lon = lat, lon # TIDAK di-reset agar start_point tetap sama
    last_cross_state = is_crossing

    # Tambahkan ke lintasan
    track_lats.append(lat)
    track_lons.append(lon)

    # Update titik & garis lintasan
    point_artist.set_data([lon], [lat])
    line_artist.set_data(track_lons, track_lats)

    # Hitung strip coverage
    if len(track_lats) > 1:
        lon_prev = track_lons[-2]
        lat_prev = track_lats[-2]
        dx, dy = lon - lon_prev, lat - lat_prev
        length = np.hypot(dx, dy)
        if length > 0:
            dx, dy = dx/length, dy/length
            nx, ny = -dy, dx
            half_w = (spotbeam_width_km / 111.0) / 2
            current_strip = Polygon([
                (lon_prev + nx*half_w, lat_prev + ny*half_w),
                (lon_prev - nx*half_w, lat_prev - ny*half_w),
                (lon      - nx*half_w, lat      - ny*half_w),
                (lon      + nx*half_w, lat      + ny*half_w)
            ])
            
            if spotbeam_union is None:
                spotbeam_union = current_strip
            else:
                # Akumulasi area cakupan
                spotbeam_union = unary_union([spotbeam_union, current_strip])
            
            x, y = current_strip.exterior.xy
            spotbeam_artist.set_data(x, y)

            if spotbeam_union.is_valid and not spotbeam_union.is_empty:
                polys = [spotbeam_union] if spotbeam_union.geom_type == "Polygon" else list(spotbeam_union.geoms)
                total_area_m2 = 0
                for poly in polys:
                    if len(poly.exterior.coords) >= 4:
                        poly_x, poly_y = poly.exterior.xy
                        area_m2, _ = geod.polygon_area_perimeter(poly_x, poly_y)
                        total_area_m2 += abs(area_m2)
                last_area_km2 = total_area_m2 / 1e6
                
                # 🎯 PENGHENTIAN BARU: Cek apakah titik awal sudah tercakup
                if start_point is not None and spotbeam_union.contains(start_point):
                    if save_counter < max_saves:
                        # Simpan baris terakhir sebelum berhenti
                        with open(csv_filename, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                sim_time.strftime('%Y-%m-%d %H:%M:%S'),
                                f"{lat:.6f}", f"{lon:.6f}", f"{alt:.2f}", f"{last_area_km2:.2f}"
                            ])
                        save_counter += 1
                        print(f"\n[INFO] Titik awal (lat={first_lat:.2f}, lon={first_lon:.2f}) TERCATAT di CSV (ke-{save_counter}) dan Simulasi Dihentikan oleh Coverage.")
                    else:
                         print(f"\n[INFO] Titik awal (lat={first_lat:.2f}, lon={first_lon:.2f}) masuk ke area spotbeam, tetapi batas CSV (5 data) sudah tercapai.")
                    
                    stop_simulation = True # Set flag untuk menghentikan animasi

    # Batasi jumlah titik lintasan (2 orbit)
    orbit_period_sec = 5520
    frame_sim_sec = (update_interval_ms/1000.0) * speedup
    max_points = int(2 * orbit_period_sec / frame_sim_sec)
    
    # 💾 PENYIMPANAN DATA PERIODE (Pengganti Mekanisme Lama)
    if len(track_lats) > max_points:
        # Jika belum dihentikan oleh kondisi coverage DAN belum mencapai batas baris
        if not stop_simulation and save_counter < max_saves:
            with open(csv_filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    sim_time.strftime('%Y-%m-%d %H:%M:%S'),
                    f"{lat:.6f}", f"{lon:.6f}", f"{alt:.2f}", f"{last_area_km2:.2f}"
                ])
            save_counter += 1
            print(f"[INFO] Data spotbeam disimpan ke CSV (ke-{save_counter}) berdasarkan batas orbit.")
            
        # Logika membersihkan lintasan
        track_lats.pop(0)
        track_lons.pop(0)

    # Update teks
    area_text.set_text(f"Cakupan spotbeam: {last_area_km2/1e3:.2f} ribu km²")
    time_text.set_text(
        f"UTC sim: {sim_time.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"lat={lat:.2f}, lon={lon:.2f}, alt={alt:.1f} km"
    )

    return (point_artist, line_artist, spotbeam_artist, time_text, area_text)

# Fungsi untuk menghentikan animasi Matplotlib (Wajib karena FuncAnimation tidak berhenti otomatis)
def check_stop():
    if stop_simulation:
        anim.event_source.stop()
        print("[INFO] Animasi Matplotlib Dihentikan.")
    else:
        fig.canvas.manager.window.after(100, check_stop)

anim = FuncAnimation(fig, update, interval=update_interval_ms, blit=True)

# Panggil pengecekan penghentian
if fig.canvas.manager:
    fig.canvas.manager.window.after(100, check_stop)

plt.show()