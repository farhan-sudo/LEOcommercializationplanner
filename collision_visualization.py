"""
Sistem Visualisasi Collision Detection Satelit dengan Debris
=============================================================
Program ini menampilkan jalur satelit dan posisi debris di peta dunia
untuk memvisualisasikan hasil prediksi collision.
"""

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from collision_prediction import (
    propagate_satellite_trajectory, 
    parse_debris_tle,
    check_collision,
    COLLISION_THRESHOLD
)


def plot_collision_detection(tle_line1, tle_line2, debris_file_path,
                             num_periods=5, time_step_minutes=1,
                             threshold=COLLISION_THRESHOLD):
    print("Memproses data untuk visualisasi...")
    
    # 1. Propagasi jalur satelit
    trajectory = propagate_satellite_trajectory(tle_line1, tle_line2, 
                                                num_periods, time_step_minutes)
    
    # 2. Deteksi kategori altitude satelit
    from collision_prediction import categorize_altitude
    avg_satellite_alt = np.mean([p['alt'] for p in trajectory])
    sat_category, sat_cat_idx = categorize_altitude(avg_satellite_alt)
    
    print(f"[INFO] Altitude rata-rata satelit: {avg_satellite_alt:.2f} km")
    print(f"[INFO] Kategori satelit: {sat_category}")
    
    # 3. Parse posisi debris dengan filter kategori yang sama dengan satelit
    if sat_cat_idx >= 0:
        print(f"[INFO] Memfilter debris untuk kategori: {sat_category}")
        debris_positions = parse_debris_tle(debris_file_path, filter_category=sat_cat_idx)
        print(f"[OK] Debris dalam kategori yang sama: {len(debris_positions)} objek")
    else:
        print(f"[INFO] Satelit di luar range LEO, menampilkan semua debris")
        debris_positions = parse_debris_tle(debris_file_path, filter_category=None)
    
    # 4. Cek collision
    result = check_collision(trajectory, debris_positions, threshold)
    
    # 5. Buat plot (3 panel tanpa grafik altitude)
    fig = plt.figure(figsize=(18, 6))
    
    # Plot 1: Jalur satelit dan semua debris (style dari debris.py)
    ax1 = fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree())
    
    # Tambahkan fitur peta (style dari debris.py)
    ax1.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
    ax1.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax1.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                 linewidth=0.5, alpha=0.5)
    ax1.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    
    # Plot debris dengan warna berdasarkan altitude (style dari debris.py)
    debris_lons = [d['lon'] for d in debris_positions]
    debris_lats = [d['lat'] for d in debris_positions]
    debris_alts = [d['alt'] for d in debris_positions]
    
    scatter = ax1.scatter(debris_lons, debris_lats, c=debris_alts, s=10, alpha=0.6,
                         cmap='jet', transform=ccrs.PlateCarree())
    
    # Tentukan jalur yang akan ditampilkan
    if result['collision']:
        # Jika ada collision, tampilkan hanya sampai collision pertama
        first_collision_idx = None
        for idx, point in enumerate(trajectory):
            if any(cp['sat_pos']['time'] == point['time'] for cp in result['collision_points']):
                first_collision_idx = idx
                break
        
        if first_collision_idx is not None:
            # Jalur sampai collision (hijau ke merah)
            trajectory_until_collision = trajectory[:first_collision_idx + 1]
            sat_lons_safe = [p['lon'] for p in trajectory_until_collision]
            sat_lats_safe = [p['lat'] for p in trajectory_until_collision]
            
            # Plot jalur dengan gradient warna (hijau -> kuning -> merah)
            for i in range(len(sat_lons_safe) - 1):
                # Gradasi warna dari hijau (awal) ke merah (collision)
                color_ratio = i / max(len(sat_lons_safe) - 1, 1)
                color = plt.cm.RdYlGn_r(color_ratio)  # Red-Yellow-Green reversed
                ax1.plot(sat_lons_safe[i:i+2], sat_lats_safe[i:i+2], 
                        color=color, linewidth=2, alpha=0.8,
                        transform=ccrs.PlateCarree())
            
            # Label untuk legend
            ax1.plot([], [], 'g-', linewidth=2, label='Jalur Satelit (Aman)', alpha=0.8)
            ax1.plot([], [], 'r-', linewidth=2, label='Titik Collision', alpha=0.8)
            
            # Plot titik collision
            collision_point = trajectory[first_collision_idx]
            ax1.scatter(collision_point['lon'], collision_point['lat'], 
                       c='red', s=200, transform=ccrs.PlateCarree(), 
                       label='COLLISION!', marker='X', zorder=7, 
                       edgecolors='black', linewidths=2)
        else:
            # Fallback jika tidak ditemukan collision point
            sat_lons = [p['lon'] for p in trajectory]
            sat_lats = [p['lat'] for p in trajectory]
            ax1.plot(sat_lons, sat_lats, 'r-', linewidth=2, alpha=0.7,
                    transform=ccrs.PlateCarree(), label='Jalur Satelit (Collision)')
    else:
        # Jika aman, tampilkan jalur penuh 5 periode dengan warna hijau
        sat_lons = [p['lon'] for p in trajectory]
        sat_lats = [p['lat'] for p in trajectory]
        ax1.plot(sat_lons, sat_lats, 'g-', linewidth=1.5, alpha=0.7,
                transform=ccrs.PlateCarree(), label='Jalur Satelit (5 Periode)')
    
    # Plot titik awal
    ax1.scatter(trajectory[0]['lon'], trajectory[0]['lat'], c='blue', s=150, 
                transform=ccrs.PlateCarree(), label='Start', marker='o', 
                zorder=5, edgecolors='white', linewidths=1.5)
    
    # Plot titik akhir (hanya jika tidak collision)
    if not result['collision']:
        ax1.scatter(trajectory[-1]['lon'], trajectory[-1]['lat'], c='darkgreen', s=150,
                    transform=ccrs.PlateCarree(), label='End (5 Periode)', marker='s', 
                    zorder=5, edgecolors='white', linewidths=1.5)
    
    # Title berbeda untuk collision dan aman, dengan info kategori
    if result['collision']:
        title = f'COLLISION TERDETEKSI\nKategori: {sat_category} ({len(debris_positions)} debris)'
        ax1.set_title(title, fontsize=12, fontweight='bold', color='red')
    else:
        title = f'AMAN - 5 Periode\nKategori: {sat_category} ({len(debris_positions)} debris)'
        ax1.set_title(title, fontsize=12, fontweight='bold', color='green')
    
    ax1.legend(loc='lower left', fontsize=9)
    
    # Plot 2: Zoom ke area collision (jika ada)
    ax2 = fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree())
    
    if result['collision'] and result['collision_points']:
        # Ambil area sekitar collision points
        collision_lons = [cp['sat_pos']['lon'] for cp in result['collision_points'][:10]]
        collision_lats = [cp['sat_pos']['lat'] for cp in result['collision_points'][:10]]
        
        # Set extent
        lon_margin = 10
        lat_margin = 10
        ax2.set_extent([min(collision_lons) - lon_margin, max(collision_lons) + lon_margin,
                       min(collision_lats) - lat_margin, max(collision_lats) + lat_margin],
                      crs=ccrs.PlateCarree())
        
        # Style dari debris.py
        ax2.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
        ax2.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
        ax2.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax2.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
        ax2.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                     linewidth=0.5, alpha=0.5)
        
        # Plot collision points
        for i, cp in enumerate(result['collision_points'][:10]):
            ax2.scatter(cp['sat_pos']['lon'], cp['sat_pos']['lat'], 
                       c='red', s=100, transform=ccrs.PlateCarree(), 
                       marker='X', zorder=5, edgecolors='black')
            ax2.scatter(cp['debris_pos']['lon'], cp['debris_pos']['lat'],
                       c='darkred', s=50, transform=ccrs.PlateCarree(),
                       marker='x', zorder=4)
        
        # Plot jalur satelit di area ini
        ax2.plot(sat_lons, sat_lats, 'b-', linewidth=2, alpha=0.7,
                transform=ccrs.PlateCarree())
        
        ax2.set_title('ZOOM: Area Collision', fontsize=14, fontweight='bold', color='red')
    else:
        # Zoom ke area jarak terdekat
        if result['closest_sat_point']:
            center_lon = result['closest_sat_point']['lon']
            center_lat = result['closest_sat_point']['lat']
            
            ax2.set_extent([center_lon - 20, center_lon + 20,
                           center_lat - 20, center_lat + 20],
                          crs=ccrs.PlateCarree())
            
            # Style dari debris.py
            ax2.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
            ax2.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
            ax2.add_feature(cfeature.COASTLINE, linewidth=0.5)
            ax2.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
            ax2.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                         linewidth=0.5, alpha=0.5)
            
            # Plot closest point
            ax2.scatter(result['closest_sat_point']['lon'], 
                       result['closest_sat_point']['lat'],
                       c='orange', s=200, transform=ccrs.PlateCarree(),
                       marker='*', zorder=5, edgecolors='black', label='Closest Point')
            
            # Plot debris terdekat
            if result['closest_debris']:
                ax2.scatter(result['closest_debris']['lon'],
                           result['closest_debris']['lat'],
                           c='red', s=100, transform=ccrs.PlateCarree(),
                           marker='x', zorder=4, label='Closest Debris')
            
            # Plot jalur satelit
            ax2.plot(sat_lons, sat_lats, 'b-', linewidth=2, alpha=0.7,
                    transform=ccrs.PlateCarree(), label='Jalur Satelit')
            
            ax2.set_title('ZOOM: Area Jarak Terdekat', fontsize=14, fontweight='bold', color='green')
            ax2.legend(loc='best', fontsize=9)
    
    # Plot 3: Histogram jarak satelit ke debris
    ax3 = fig.add_subplot(1, 3, 3)
    
    # Tentukan trajectory untuk histogram
    if result['collision']:
        # Sampai collision pertama
        first_collision_idx = None
        for idx, point in enumerate(trajectory):
            if any(cp['sat_pos']['time'] == point['time'] for cp in result['collision_points']):
                first_collision_idx = idx
                break
        
        if first_collision_idx is not None:
            histogram_trajectory = trajectory[:first_collision_idx + 1]
        else:
            histogram_trajectory = trajectory
    else:
        histogram_trajectory = trajectory
    
    # Hitung semua jarak (hanya untuk trajectory yang ditampilkan)
    all_distances = []
    sample_rate = max(1, len(histogram_trajectory) // 100)  # Sample untuk efisiensi
    for sat_pos in histogram_trajectory[::sample_rate]:
        for debris in debris_positions:
            from collision_prediction import calculate_distance
            distance = calculate_distance(sat_pos, debris)
            all_distances.append(distance)
    
    # Buat histogram dengan warna berbeda
    hist_color = 'lightcoral' if result['collision'] else 'lightgreen'
    ax3.hist(all_distances, bins=50, color=hist_color, edgecolor='black', alpha=0.7)
    ax3.axvline(threshold, color='red', linestyle='--', linewidth=2, 
               label=f'Collision Threshold ({threshold} km)')
    ax3.axvline(result['min_distance'], color='darkred' if result['collision'] else 'darkgreen', 
               linestyle='--', linewidth=2,
               label=f'Min Distance ({result["min_distance"]:.2f} km)')
    ax3.set_xlabel('Jarak (km)', fontsize=11)
    ax3.set_ylabel('Frekuensi', fontsize=11)
    
    if result['collision']:
        ax3.set_title('Distribusi Jarak - Sampai Collision', fontsize=12, fontweight='bold', color='red')
    else:
        ax3.set_title('Distribusi Jarak - 5 Periode Penuh', fontsize=12, fontweight='bold', color='green')
    
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_yscale('log')  # Log scale untuk visualisasi lebih baik
    
    # Tambahkan status di atas figure dengan info periode
    if result['collision']:
        # Hitung waktu sampai collision pertama
        first_collision_idx = None
        for idx, point in enumerate(trajectory):
            if any(cp['sat_pos']['time'] == point['time'] for cp in result['collision_points']):
                first_collision_idx = idx
                break
        
        if first_collision_idx is not None:
            time_to_collision = (trajectory[first_collision_idx]['time'] - trajectory[0]['time']).total_seconds() / 60
            status_text = f"STATUS: BAHAYA - COLLISION TERDETEKSI SETELAH {time_to_collision:.1f} MENIT"
            detail_text = f"Total {result['collision_count']} Collision Points | Jarak Terdekat: {result['min_distance']:.2f} km"
        else:
            status_text = f"STATUS: BAHAYA - {result['collision_count']} COLLISION TERDETEKSI"
            detail_text = f"Jarak Terdekat: {result['min_distance']:.2f} km"
        status_color = 'red'
    else:
        status_text = "STATUS: SUKSES - AMAN DARI COLLISION (5 PERIODE ORBIT LENGKAP)"
        detail_text = f"Jarak Terdekat dengan Debris: {result['min_distance']:.2f} km | Margin Keamanan: {result['min_distance'] - threshold:.2f} km"
        status_color = 'green'
    
    fig.suptitle(f'{status_text}\n{detail_text}',
                fontsize=14, fontweight='bold', color=status_color, y=1.05)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    print("Visualisasi selesai!")
    plt.show()
    
    return result


def main():
    """
    Fungsi main untuk visualisasi
    """
    print("=" * 70)
    print("SISTEM VISUALISASI COLLISION DETECTION")
    print("=" * 70)
    print()
    
    print("Masukkan TLE satelit (3 baris: nama, line1, line2)")
    print("Atau tekan Enter untuk menggunakan contoh default")
    print()
    
    # Input TLE dari user
    satellite_name = input("Baris 0 (Nama satelit): ").strip()
    
    if satellite_name == "":
        # Gunakan contoh default
        print("Menggunakan contoh default dari file TLE.txt")
        print()
        
        # Baca contoh dari TLE.txt
        try:
            with open("TLE.txt", 'r') as f:
                lines = f.readlines()
            
            # Ambil TLE pertama yang valid
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    name = lines[i].strip()
                    tle_line1 = lines[i + 1].strip()
                    tle_line2 = lines[i + 2].strip()
                    
                    if tle_line1.startswith('1 ') and tle_line2.startswith('2 '):
                        print(f"Menggunakan satelit: {name}")
                        break
        except FileNotFoundError:
            # Default fallback
            print("File TLE.txt tidak ditemukan, menggunakan default hardcoded")
            tle_line1 = "1 00011U 59001A   24001.00000000  .00000000  00000-0  00000-0 0  9999"
            tle_line2 = "2 00011  32.8771 348.0000 1472668 325.0000  15.0000  0.19000000000000"
    else:
        tle_line1 = input("Baris 1: ").strip()
        tle_line2 = input("Baris 2: ").strip()
    
    print()
    
    # Path ke file debris
    debris_file = "FENGYUN debris.txt"
    
    # Jalankan visualisasi
    result = plot_collision_detection(
        tle_line1,
        tle_line2,
        debris_file,
        num_periods=5,
        time_step_minutes=2,  # 2 menit untuk visualisasi lebih cepat
        threshold=5.0
    )
    
    return result


if __name__ == "__main__":
    main()
