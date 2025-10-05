import numpy as np
import random
from sgp4.api import Satrec, jday   
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for separate window
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime

files = [
    'FENGYUN debris.txt',]

earth_radius = 6371  # in km
mu = 398600.4418     # Earth's gravitational parameter in km^3/s^2

def parse_tle_file(tle_file_path, label):
    data = []
    labels = []
    fp = tle_file_path  # Langsung gunakan path file
    with open(fp, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            if i + 2 >= len(lines):  # Ensure we have both lines
                break

            line1 = lines[i+1].strip()
            line2 = lines[i + 2].strip()
            satellite = Satrec.twoline2rv(line1, line2)
            sat_id = line1[2:7].strip()
            eccentricity = satellite.ecco
            inclination = satellite.inclo
            raan = satellite.nodeo
            arg_perigee = satellite.argpo
            mean_anomaly = satellite.mo
            mean_motion = satellite.no_kozai
            semi_major_axis = 6378.1 / (1 - satellite.ecco)
            altitude = semi_major_axis - earth_radius
            perigee = semi_major_axis * (1 - eccentricity)
            apogee = semi_major_axis * (1+eccentricity)
            orbital_period = 86400/mean_motion
            
            jd, fr = jday(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day,
                          datetime.utcnow().hour, datetime.utcnow().minute, datetime.utcnow().second)

            e, r, v = satellite.sgp4(jd, fr)
            
            distance_from_center = np.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
            velocity_magnitude = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            specific_orbital_energy = (velocity_magnitude**2)/2 - (mu/distance_from_center)
            data.append({
                'sat_id': sat_id,
                'eccentricity': eccentricity,
                'inclination': inclination,
                'raan': raan,
                'arg_perigee': arg_perigee,
                'mean_anomaly': mean_anomaly,
                'mean_motion': mean_motion,
                'semi_major_axis': semi_major_axis,
                'x': r[0],
                'y': r[1],
                'z': r[2],
                'vx': v[0],
                'vy': v[1],
                'vz': v[2],
                'altitude': altitude,
                'perigee': perigee,
                'apogee': apogee,
                'orbital_period': orbital_period,
                'distance_from_center': distance_from_center,
                'specific_orbital_energy': specific_orbital_energy,
                'velocity_magnitude': velocity_magnitude,
                'label':label
            })
            labels.append(label)
    return data, labels

# Fungsi untuk konversi ECI ke Lat/Lon
def eci_to_latlon(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.degrees(np.arcsin(z / r))
    lon = np.degrees(np.arctan2(y, x))
    altitude = r - 6371.0  # Radius Bumi dalam km
    return lat, lon, altitude

def categorize_altitude(altitude):
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

# Baca data dari TLE file
print("read from TLE file...")
debris_data, debris_labels = parse_tle_file('FENGYUN debris.txt', 'FENGYUN_1C')

# Konversi ke lat/lon dan kategorisasi
debris_info = []
for debris in debris_data:
    x, y, z = debris['x'], debris['y'], debris['z']
    lat, lon, alt = eci_to_latlon(x, y, z)
    category, cat_idx = categorize_altitude(alt)
    
    debris_info.append({
        'sat_id': debris.get('sat_id', 'Unknown'),
        'lat': lat,
        'lon': lon,
        'altitude': alt,
        'category': category,
        'cat_idx': cat_idx,
        'eccentricity': debris['eccentricity'],
        'inclination': debris['inclination'],
        'perigee': debris['perigee'],
        'apogee': debris['apogee']
    })

print(f"Debris Total: {len(debris_info)}")
print(f"Debris in range of LEO (160-2000 km): {len([d for d in debris_info if d['cat_idx'] >= 0])}")

# Visualisasi interaktif dengan pemilihan kategori
def plot_debris_map(selected_categories=None, show_all=False):
    if selected_categories is None:
        selected_categories = [0, 1, 2, 3, 4]  # Semua kategori
    
    fig = plt.figure(figsize=(18, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Tambahkan fitur peta
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, 
                 linewidth=0.5, alpha=0.5)
    
    # Warna untuk setiap kategori
    colors = ['#FF0000', '#FF8800', '#FFFF00', '#00FF00', '#0000FF']
    category_names = ['160-528 km', '528-896 km', '896-1264 km', '1264-1632 km', '1632-2000 km']
    
    # Plot debris berdasarkan kategori yang dipilih
    if show_all:
        # Tampilkan semua debris termasuk yang di luar range
        all_debris = [d for d in debris_info]
        lats = [d['lat'] for d in all_debris]
        lons = [d['lon'] for d in all_debris]
        alts = [d['altitude'] for d in all_debris]
        
        scatter = ax.scatter(lons, lats, c=alts, s=20, alpha=0.6, 
                            cmap='jet', transform=ccrs.PlateCarree())
        cbar = plt.colorbar(scatter, ax=ax, orientation='horizontal', 
                           pad=0.05, shrink=0.8)
        cbar.set_label('Height (km)', fontsize=12)
    else:
        for cat_idx in selected_categories:
            debris_in_cat = [d for d in debris_info if d['cat_idx'] == cat_idx]
            if debris_in_cat:
                lats = [d['lat'] for d in debris_in_cat]
                lons = [d['lon'] for d in debris_in_cat]
                ax.scatter(lons, lats, c=colors[cat_idx], s=30, alpha=0.7, 
                          transform=ccrs.PlateCarree(), 
                          label=f"{category_names[cat_idx]} ({len(debris_in_cat)} debris)")
    
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    
    if not show_all:
        plt.legend(loc='lower left', fontsize=10, framealpha=0.9)
    
    fig.suptitle('Debris Distribution in Low Earth Orbit (LEO 160-2000 km)', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig

print("\nPlot 1: Category 160-528 km")
fig1 = plot_debris_map(selected_categories=[0])
plt.show()

print("\nPlot 2: Category 528-896 km")
fig2 = plot_debris_map(selected_categories=[1])
plt.show()

print("\nPlot 3: Category 896-1264 km")
fig3 = plot_debris_map(selected_categories=[2])
plt.show()

print("\nPlot 4: Category 1264-1632 km")
fig4 = plot_debris_map(selected_categories=[3])
plt.show()

print("\nPlot 5: Category Tinggi (1632-2000 km)")
fig5 = plot_debris_map(selected_categories=[4])
plt.show()

print("\nSDebris Statistics per category")
for i, cat_name in enumerate(['160-528 km', '528-896 km', '896-1264 km', '1264-1632 km', '1632-2000 km']):
    count = len([d for d in debris_info if d['cat_idx'] == i])
    if count > 0:
        avg_alt = np.mean([d['altitude'] for d in debris_info if d['cat_idx'] == i])
        print(f"{cat_name}: {count} debris (Height avg: {avg_alt:.2f} km)")
    else:
        print(f"{cat_name}: {count} debris")

out_of_range = len([d for d in debris_info if d['cat_idx'] == -1])
print(f"\nDebris di luar range LEO: {out_of_range}")

print("\nSample Data (5 debris pertama)")
for i, debris in enumerate(debris_info[:5]):
    print(f"\nDebris #{i+1}:")
    print(f"  ID: {debris['sat_id']}")
    print(f"  Posisi: Lat={debris['lat']:.2f}°, Lon={debris['lon']:.2f}°")
    print(f"  Ketinggian: {debris['altitude']:.2f} km")
    print(f"  Kategori: {debris['category']}")
    print(f"  Eccentricity: {debris['eccentricity']:.6f}")
    print(f"  Inclination: {np.degrees(debris['inclination']):.2f}°")