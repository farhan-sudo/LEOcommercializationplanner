# 🚀 Quick Start Guide - Satellite Tracking System

## Cara Termudah untuk Memulai

### Windows (Menggunakan start.bat)

1. **Buka Command Prompt atau PowerShell**
   - Tekan `Win + R`, ketik `cmd`, tekan Enter

2. **Navigasi ke folder project**
   ```cmd
   cd c:\Users\farhan\Projects\websitespaceapps\appss
   ```

3. **Jalankan start.bat**
   ```cmd
   start.bat
   ```
   
   Script ini akan otomatis:
   - Membuat virtual environment (jika belum ada)
   - Menginstall dependencies
   - Menjalankan Flask server

4. **Buka Browser**
   - Ketik: `http://localhost:5000`

### Manual Installation

Jika start.bat tidak berfungsi, ikuti langkah manual:

#### 1. Install Python
Pastikan Python 3.8+ terinstall:
```cmd
python --version
```

#### 2. Buat Virtual Environment
```cmd
python -m venv venv
```

#### 3. Aktifkan Virtual Environment
**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

#### 4. Install Dependencies
```cmd
pip install -r requirements.txt
```

**Jika ada error dengan Cartopy**, coba:
```cmd
pip install --upgrade pip setuptools wheel
pip install cartopy --no-binary cartopy
```

Atau download wheel dari: https://www.lfd.uci.edu/~gohlke/pythonlibs/#cartopy

#### 5. Jalankan Aplikasi
```cmd
python app.py
```

#### 6. Akses di Browser
Buka: `http://localhost:5000`

## 🎯 Fitur-Fitur Utama

### 1. Dashboard (Halaman Utama)
- Overview semua fitur
- Statistik sistem
- Link ke semua modul

### 2. Collision Prediction
**Cara Menggunakan:**
1. Klik "Collision Prediction" di menu
2. Klik "Load Example (ISS)" untuk data contoh
3. Atau masukkan TLE manual:
   ```
   Line 1: 1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997
   Line 2: 2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172
   ```
4. Atur parameter:
   - Number of Periods: 5 (berapa orbit yang diprediksi)
   - Time Step: 1 menit (interval sampling)
   - Threshold: 5.0 km (jarak minimum aman)
5. Klik "Predict Collision"

**Output:**
- Status: SAFE atau DANGER
- Jarak minimum dengan debris
- Detail titik terdekat
- Tabel collision points (jika ada)

### 3. Debris Visualization
**Cara Menggunakan:**
1. Klik "Debris Map" di menu
2. Pilih kategori altitude:
   - 160-528 km (Very Low LEO)
   - 528-896 km (Low LEO)
   - 896-1264 km (Mid LEO)
   - 1264-1632 km (High LEO)
   - 1632-2000 km (Very High LEO)
   - Atau "All Categories"
3. Klik "Generate Map"

**Output:**
- Peta distribusi debris (gambar)
- Peta interaktif (Leaflet)
- Statistik jumlah debris per kategori

### 4. Satellite Tracking
**Cara Menggunakan:**
1. Klik "Satellite Tracking" di menu
2. Masukkan TLE satelit atau load example
3. Klik "Track Satellite"
4. Lihat posisi real-time di peta
5. (Opsional) Aktifkan "Auto Update" untuk tracking otomatis setiap 5 detik

**Output:**
- Peta dengan marker satelit
- Latitude, Longitude, Altitude
- Posisi ECI (X, Y, Z)
- Periode orbital

### 5. Passing Time Calculator
**Cara Menggunakan:**
1. Klik "Passing Time" di menu
2. Masukkan data satelit (TLE)
3. Masukkan lokasi observer:
   - Latitude: -6.200000 (Jakarta)
   - Longitude: 106.816666
   - Elevation: 5 meter
   - Min Elevation: 10° (sudut minimum di atas horizon)
4. Atau gunakan "Popular Locations"
5. Klik "Calculate Passes"

**Output:**
- Daftar passing dalam 24 jam ke depan
- AOS (Acquisition of Signal) - waktu muncul
- LOS (Loss of Signal) - waktu hilang
- Max Altitude - sudut tertinggi
- Azimuth - arah kompas
- Duration - durasi visible

## 🔧 Troubleshooting

### Error: "Address already in use"
**Solusi:** Port 5000 sudah digunakan. Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```
Lalu akses: `http://localhost:8080`

### Error: "ModuleNotFoundError"
**Solusi:** Install ulang dependencies:
```cmd
pip install -r requirements.txt --force-reinstall
```

### Map tidak muncul
**Solusi:** 
- Cek koneksi internet (map tiles dari OpenStreetMap)
- Clear browser cache
- Coba browser lain

### TLE data error
**Solusi:**
- Pastikan TLE format benar (2 baris, starts with '1' dan '2')
- Gunakan TLE terbaru dari https://celestrak.org/
- TLE lama bisa menyebabkan error propagasi

### Cartopy installation error (Windows)
**Solusi:**
1. Download pre-built wheel:
   - Buka: https://www.lfd.uci.edu/~gohlke/pythonlibs/#cartopy
   - Download sesuai Python version (contoh: Cartopy‑0.22.0‑cp312‑cp312‑win_amd64.whl)
   
2. Install wheel:
   ```cmd
   pip install Cartopy‑0.22.0‑cp312‑cp312‑win_amd64.whl
   ```

## 📱 Tips Penggunaan

### Mendapatkan TLE Terbaru
1. **CelesTrak**: https://celestrak.org/
2. **Space-Track**: https://www.space-track.org/ (perlu registrasi)
3. **N2YO**: https://www.n2yo.com/

### Satelit Populer untuk Testing
- **ISS (25544)**: International Space Station
- **HST (20580)**: Hubble Space Telescope
- **NOAA satellites**: Weather satellites
- **Starlink**: SpaceX constellation

### Best Practices
1. **Collision Prediction**: Gunakan 5-10 periode untuk akurasi
2. **Time Step**: 1-2 menit untuk detail, 5-10 menit untuk cepat
3. **Passing Time**: Min elevation 10° untuk visibility baik
4. **Debris Map**: Filter by category untuk performa lebih baik

## 🎓 Penjelasan Istilah

- **TLE (Two-Line Element)**: Format standar untuk data orbit satelit
- **SGP4**: Model propagasi orbit satelit
- **LEO**: Low Earth Orbit (160-2000 km)
- **ECI**: Earth-Centered Inertial coordinate system
- **AOS/LOS**: Acquisition/Loss of Signal
- **Azimuth**: Arah horizontal (0°=N, 90°=E, 180°=S, 270°=W)
- **Elevation**: Sudut vertikal dari horizon (0°=horizon, 90°=zenith)

## 📞 Bantuan Lebih Lanjut

Jika masih ada masalah:
1. Cek log di terminal/command prompt
2. Pastikan semua file ada (terutama `FENGYUN debris.txt`)
3. Restart Flask server
4. Clear browser cache

---

**Selamat Menggunakan! 🚀🛰️**
