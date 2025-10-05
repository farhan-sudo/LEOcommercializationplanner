import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import math

# Konstanta
EARTH_RADIUS = 6371.0  # km
COLLISION_THRESHOLD = 5.0  # km - jarak minimum aman
MU = 398600.4418  # km^3/s^2 - Earth gravitational parameter


def calculate_orbital_period(tle_line1, tle_line2):
    
    mean_motion = float(tle_line2[52:63])  # rev/day
    
    period = 1440.0 / mean_motion  # 1440 menit = 1 hari
    
    return period


def propagate_satellite_trajectory(tle_line1, tle_line2, num_periods=5, time_step_minutes=1):
    # Parse TLE
    satellite = Satrec.twoline2rv(tle_line1, tle_line2)
    
    # Hitung periode orbit
    period_minutes = calculate_orbital_period(tle_line1, tle_line2)
    
    # Total waktu prediksi
    total_time = period_minutes * num_periods
    
    # Jumlah step
    num_steps = int(total_time / time_step_minutes)
    
    # Waktu mulai (sekarang)
    start_time = datetime.utcnow()
    
    trajectory = []
    
    for i in range(num_steps):
        # Hitung waktu untuk step ini
        current_time = start_time + timedelta(minutes=i * time_step_minutes)
        jd, fr = jday(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second)
        
        # Propagasi posisi satelit
        error, position, velocity = satellite.sgp4(jd, fr)
        
        if error == 0:  # Tidak ada error
            x, y, z = position
            
            # Konversi ECI ke Lat/Lon
            lat, lon, alt = eci_to_latlon(x, y, z)
            
            trajectory.append({
                'time': current_time,
                'x': x,
                'y': y,
                'z': z,
                'lat': lat,
                'lon': lon,
                'alt': alt
            })
    
    return trajectory


def eci_to_latlon(x, y, z):
    
    # Jarak dari pusat bumi
    r = math.sqrt(x**2 + y**2 + z**2)
    
    # Altitude (tinggi dari permukaan bumi)
    altitude = r - EARTH_RADIUS
    
    # Latitude
    latitude = math.degrees(math.asin(z / r))
    
    # Longitude
    longitude = math.degrees(math.atan2(y, x))
    
    return latitude, longitude, altitude


def categorize_altitude(altitude):
    """
    Kategorisasi altitude debris berdasarkan range LEO
    """
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


def parse_debris_tle(tle_file_path, filter_category=None):
    """
    Parse debris TLE dengan optional filtering berdasarkan kategori altitude
    
    Parameters:
    -----------
    tle_file_path : str
        Path ke file TLE debris
    filter_category : int, optional
        Kategori altitude untuk filter (0-4), None = tampilkan semua
        0: 160-528 km
        1: 528-896 km
        2: 896-1264 km
        3: 1264-1632 km
        4: 1632-2000 km
    """
    debris_positions = []
    
    try:
        with open(tle_file_path, 'r') as file:
            lines = file.readlines()
        
        current_time = datetime.utcnow()
        jd, fr = jday(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second)
        
        # Proses setiap TLE (3 baris: nama, line1, line2)
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()
                
                try:
                    # Parse TLE
                    debris = Satrec.twoline2rv(line1, line2)
                    
                    # Propagasi ke waktu sekarang
                    error, position, velocity = debris.sgp4(jd, fr)
                    
                    if error == 0:
                        x, y, z = position
                        lat, lon, alt = eci_to_latlon(x, y, z)
                        
                        # Kategorisasi altitude
                        category, cat_idx = categorize_altitude(alt)
                        
                        # Filter berdasarkan kategori jika diminta
                        if filter_category is None or cat_idx == filter_category:
                            debris_positions.append({
                                'x': x,
                                'y': y,
                                'z': z,
                                'lat': lat,
                                'lon': lon,
                                'alt': alt,
                                'category': category,
                                'cat_idx': cat_idx
                            })
                except Exception as e:
                    continue
    
    except FileNotFoundError:
        print(f"Error: File {tle_file_path} tidak ditemukan")
        return []
    
    return debris_positions


def calculate_distance(pos1, pos2):
    dx = pos1['x'] - pos2['x']
    dy = pos1['y'] - pos2['y']
    dz = pos1['z'] - pos2['z']
    
    return math.sqrt(dx**2 + dy**2 + dz**2)


def check_collision(satellite_trajectory, debris_positions, threshold=COLLISION_THRESHOLD):
    min_distance = float('inf')
    closest_sat_point = None
    closest_debris = None
    collision_count = 0
    collision_points = []
    
    # Cek setiap titik di jalur satelit
    for sat_pos in satellite_trajectory:
        # Cek terhadap semua debris
        for debris in debris_positions:
            distance = calculate_distance(sat_pos, debris)
            
            # Update jarak minimum
            if distance < min_distance:
                min_distance = distance
                closest_sat_point = sat_pos
                closest_debris = debris
            
            # Cek apakah collision (jarak < threshold)
            if distance < threshold:
                collision_count += 1
                collision_points.append({
                    'time': sat_pos['time'],
                    'distance': distance,
                    'sat_pos': sat_pos,
                    'debris_pos': debris
                })
    
    result = {
        'collision': collision_count > 0,
        'collision_count': collision_count,
        'min_distance': min_distance,
        'closest_sat_point': closest_sat_point,
        'closest_debris': closest_debris,
        'collision_points': collision_points
    }
    
    return result


def predict_satellite_collision(tle_line1, tle_line2, debris_file_path, 
                                  num_periods=5, time_step_minutes=1, 
                                  threshold=COLLISION_THRESHOLD):
    print("=" * 70)
    print("SISTEM PREDIKSI COLLISION SATELIT DENGAN DEBRIS")
    print("=" * 70)
    print()
    
    # 1. Hitung periode orbit
    period = calculate_orbital_period(tle_line1, tle_line2)
    print(f"[OK] Periode orbit satelit: {period:.2f} menit ({period/60:.2f} jam)")
    print(f"[OK] Durasi prediksi: {num_periods} periode = {period*num_periods:.2f} menit ({period*num_periods/60:.2f} jam)")
    print()
    
    # 2. Propagasi jalur satelit
    print("[INFO] Memprediksi jalur satelit...")
    trajectory = propagate_satellite_trajectory(tle_line1, tle_line2, 
                                                num_periods, time_step_minutes)
    print(f"[OK] Total {len(trajectory)} titik posisi diprediksi")
    print()
    
    # 3. Parse posisi debris
    print("[INFO] Memuat data debris...")
    debris_positions = parse_debris_tle(debris_file_path)
    print(f"[OK] Total {len(debris_positions)} debris terdeteksi")
    print()
    
    # 4. Cek collision
    print(f"[INFO] Mengecek collision (threshold: {threshold} km)...")
    result = check_collision(trajectory, debris_positions, threshold)
    print()
    
    # 5. Tampilkan hasil
    print("=" * 70)
    print("HASIL PREDIKSI:")
    print("=" * 70)
    
    if result['collision']:
        print("[BAHAYA] STATUS: BAHAYA - COLLISION TERDETEKSI!")
        print()
        print(f"   Jumlah collision point: {result['collision_count']}")
        print(f"   Jarak terdekat dengan debris: {result['min_distance']:.2f} km")
        print()
        
        if result['closest_sat_point']:
            print("   Detail titik terdekat:")
            print(f"   - Waktu: {result['closest_sat_point']['time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"   - Posisi satelit: ({result['closest_sat_point']['x']:.2f}, "
                  f"{result['closest_sat_point']['y']:.2f}, {result['closest_sat_point']['z']:.2f}) km")
            print(f"   - Lat/Lon: {result['closest_sat_point']['lat']:.2f}°, "
                  f"{result['closest_sat_point']['lon']:.2f}°")
            print(f"   - Altitude: {result['closest_sat_point']['alt']:.2f} km")
        
        # Tampilkan beberapa collision point pertama
        if result['collision_points']:
            print()
            print(f"   {min(5, len(result['collision_points']))} Collision point pertama:")
            for i, cp in enumerate(result['collision_points'][:5], 1):
                print(f"   {i}. Waktu: {cp['time'].strftime('%H:%M:%S')}, "
                      f"Jarak: {cp['distance']:.2f} km")
    else:
        print("[SUKSES] STATUS: SUKSES - AMAN DARI COLLISION!")
        print()
        print(f"   Jarak terdekat dengan debris: {result['min_distance']:.2f} km")
        print(f"   Margin keamanan: {result['min_distance'] - threshold:.2f} km")
        print()
        
        if result['closest_sat_point']:
            print("   Detail jarak terdekat:")
            print(f"   - Waktu: {result['closest_sat_point']['time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"   - Lat/Lon: {result['closest_sat_point']['lat']:.2f}°, "
                  f"{result['closest_sat_point']['lon']:.2f}°")
            print(f"   - Altitude: {result['closest_sat_point']['alt']:.2f} km")
    
    print("=" * 70)
    print()
    
    # Return result dengan TLE untuk visualisasi
    result['tle_line1'] = tle_line1
    result['tle_line2'] = tle_line2
    result['debris_file'] = debris_file_path
    result['num_periods'] = num_periods
    result['time_step_minutes'] = time_step_minutes
    result['threshold'] = threshold
    
    return result


def main():
    print("Masukkan TLE satelit (3 baris: nama, line1, line2)")
    print("Atau tekan Enter untuk menggunakan contoh default")
    print()
    
    satellite_name = input("Baris 0 (Nama satelit): ").strip()
    
    if satellite_name == "":
        print("Menggunakan contoh default: VANGUARD 2")
        satellite_name = "VANGUARD 2"
        tle_line1 = "1 00011U 59001A   24001.00000000  .00000000  00000-0  00000-0 0  9999"
        tle_line2 = "2 00011  32.8771 348.0000 1472668 325.0000  15.0000  0.19000000000000"
    else:
        tle_line1 = input("Baris 1: ").strip()
        tle_line2 = input("Baris 2: ").strip()
    
    print()
    
    debris_file = "FENGYUN debris.txt"
    
    result = predict_satellite_collision(
        tle_line1, 
        tle_line2, 
        debris_file,
        num_periods=5,
        time_step_minutes=1,  # Sample setiap 1 menit
        threshold=5.0  # 5 km threshold
    )
    
    # Tanya user apakah ingin melihat visualisasi
    print()
    print("=" * 70)
    show_viz = input("Tampilkan visualisasi grafis? (Y/n): ").strip().lower()
    
    if show_viz != 'n':
        print()
        print("[INFO] Membuka visualisasi...")
        print("   (Jendela grafik akan muncul dalam beberapa detik)")
        print()
        
        try:
            # Import dan jalankan visualisasi
            from collision_visualization import plot_collision_detection
            
            plot_collision_detection(
                tle_line1,
                tle_line2,
                debris_file,
                num_periods=5,
                time_step_minutes=2,  # Lebih cepat untuk visualisasi
                threshold=5.0
            )
        except Exception as e:
            print(f"[ERROR] Error saat membuka visualisasi: {str(e)}")
            print("   Pastikan semua dependencies terinstall (matplotlib, cartopy)")
    
    return result


if __name__ == "__main__":
    main()
