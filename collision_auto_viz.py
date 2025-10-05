"""
Sistem Collision Detection + Auto Visualisasi (3 Window Terpisah)
==================================================================
Program ini menggabungkan analisis collision dengan visualisasi otomatis
menggunakan 3 window terpisah tanpa perlu input TLE ulang.
"""

from collision_prediction import predict_satellite_collision, COLLISION_THRESHOLD
from collision_visualization_3windows import plot_collision_detection


def run_auto_detection_and_viz(tle_line1, tle_line2, debris_file_path,
                                num_periods=5, time_step_minutes=1,
                                threshold=COLLISION_THRESHOLD):
    """
    Menjalankan prediksi collision dan langsung visualisasi otomatis
    dengan 3 window terpisah.
    
    Parameters:
    -----------
    tle_line1 : str
        Baris pertama TLE satelit
    tle_line2 : str
        Baris kedua TLE satelit
    debris_file_path : str
        Path ke file TLE debris
    num_periods : int
        Jumlah periode orbit untuk prediksi
    time_step_minutes : float
        Interval waktu sampling (menit)
    threshold : float
        Jarak minimum aman (km)
    
    Returns:
    --------
    dict
        Hasil analisis collision
    """
    print()
    print("=" * 80)
    print(" SISTEM COLLISION DETECTION + AUTO VISUALISASI (3 WINDOW TERPISAH) ")
    print("=" * 80)
    print()
    
    # Langkah 1: Analisis Collision (Text Output)
    print("[INFO] Langkah 1: Menjalankan Analisis Collision...")
    print("-" * 80)
    result = predict_satellite_collision(
        tle_line1, 
        tle_line2, 
        debris_file_path,
        num_periods=num_periods,
        time_step_minutes=time_step_minutes,
        threshold=threshold
    )
    
    print()
    print("-" * 80)
    print("[OK] Analisis Selesai!")
    print()
    
    # Langkah 2: Visualisasi Otomatis (3 Window Terpisah)
    print("[INFO] Langkah 2: Membuka Visualisasi (3 Window Terpisah)...")
    print("-" * 80)
    print()
    
    # Langsung visualisasi tanpa input ulang
    plot_collision_detection(
        tle_line1,
        tle_line2,
        debris_file_path,
        num_periods=num_periods,
        time_step_minutes=time_step_minutes,
        threshold=threshold
    )
    
    print()
    print("=" * 80)
    print("[OK] Program Selesai!")
    print("=" * 80)
    print()
    
    return result


def main():
    """
    Fungsi main untuk sistem auto detection + visualisasi
    """
    print()
    print("=" * 80)
    print(" INPUT TLE SATELIT ")
    print("=" * 80)
    print()
    print("Masukkan TLE satelit (3 baris: nama, line1, line2)")
    print("Atau tekan Enter untuk menggunakan contoh default dari TLE.txt")
    print()
    
    # Input TLE dari user
    satellite_name = input("Baris 0 (Nama satelit): ").strip()
    
    if satellite_name == "":
        # Gunakan contoh default dari TLE.txt
        print()
        print("[INFO] Menggunakan contoh default dari file TLE.txt")
        
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
                        print(f"[OK] Menggunakan satelit: {name}")
                        break
        except FileNotFoundError:
            print("[ERROR] File TLE.txt tidak ditemukan!")
            print("[INFO] Menggunakan default hardcoded")
            tle_line1 = "1 00011U 59001A   24001.00000000  .00000000  00000-0  00000-0 0  9999"
            tle_line2 = "2 00011  32.8771 348.0000 1472668 325.0000  15.0000  0.19000000000000"
    else:
        tle_line1 = input("Baris 1: ").strip()
        tle_line2 = input("Baris 2: ").strip()
        print()
        print(f"[OK] TLE satelit diterima: {satellite_name}")
    
    # Path ke file debris
    debris_file = "FENGYUN debris.txt"
    
    # Parameter prediksi
    num_periods = 5
    time_step = 2  # 2 menit untuk balance speed vs accuracy
    threshold = 5.0  # 5 km
    
    print()
    print("-" * 80)
    print("PARAMETER PREDIKSI:")
    print(f"  - Jumlah periode orbit    : {num_periods} periode")
    print(f"  - Interval sampling       : {time_step} menit")
    print(f"  - Collision threshold     : {threshold} km")
    print(f"  - File debris             : {debris_file}")
    print("-" * 80)
    
    # Jalankan auto detection + visualisasi
    result = run_auto_detection_and_viz(
        tle_line1,
        tle_line2,
        debris_file,
        num_periods=num_periods,
        time_step_minutes=time_step,
        threshold=threshold
    )
    
    return result


if __name__ == "__main__":
    main()
