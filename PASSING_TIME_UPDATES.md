# 🛰️ Passing Time Feature - Updates & Enhancements

## ✨ Fitur Baru yang Ditambahkan

### 1. **Kolom Waktu AOS dan LOS yang Detail**
- **AOS (Acquisition of Signal)**: Waktu satelit muncul di atas minimum elevation
- **LOS (Loss of Signal)**: Waktu satelit menghilang di bawah minimum elevation
- **Maximum Elevation Time**: Waktu saat satelit berada di titik tertinggi

### 2. **Tampilan Visual yang Ditingkatkan**
- Card terpisah untuk AOS, Max Elevation, dan LOS
- Color coding berdasarkan kualitas pass:
  - 🟢 Green (60°+): Excellent
  - 🔵 Blue (45-60°): Very Good
  - 🔷 Cyan (30-45°): Good
  - 🟡 Yellow (20-30°): Fair
  - ⚪ Gray (<20°): Low

### 3. **Timeline Table**
Setiap pass memiliki tabel timeline yang menampilkan:
- Event AOS Start dengan waktu dan deskripsi
- Maximum elevation dengan koordinat lengkap
- Event LOS End dengan waktu dan deskripsi

### 4. **Informasi Tambahan**
- **Direction dari Azimuth**: 
  - Konversi azimuth (0-360°) ke arah mata angin (N, NE, E, SE, dll)
  - Contoh: 45° = NE (Northeast), 180° = S (South)
- **Duration**: Total waktu visibility dalam menit
- **Azimuth**: Arah kompas saat maximum elevation

### 5. **Summary Statistics**
Dashboard statistik yang menampilkan:
- Total jumlah passes dalam 24 jam
- Total durasi visibility (menit)
- Rata-rata durasi per pass
- Maximum elevation terbaik

### 6. **Export Functionality**
- Tombol "Export Data" untuk download CSV
- CSV berisi semua informasi pass termasuk AOS, LOS, elevation, azimuth
- Format yang mudah dibuka di Excel atau Google Sheets

### 7. **Enhanced Documentation**
Penjelasan lengkap tentang:
- Apa itu AOS, LOS, Elevation, Azimuth, Duration
- Pass Quality Guide (rating berdasarkan elevation)
- Observation Tips untuk observasi satelit

## 📊 Format Data yang Ditampilkan

### Untuk Setiap Pass:
```
┌─────────────────────────────────────────────────────────┐
│ Pass #1 - Max Elevation: 75.3°                          │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌──────────────┐  ┌─────────────┐    │
│ │ AOS         │  │ Max Elev     │  │ LOS         │    │
│ │ 2025-10-05  │  │ 15:23:45 UTC │  │ 2025-10-05  │    │
│ │ 15:20:12    │  │ 75.3° @ 180° │  │ 15:27:18    │    │
│ │ UTC         │  │ (South)      │  │ UTC         │    │
│ └─────────────┘  └──────────────┘  └─────────────┘    │
│                                                         │
│ Duration: 7.10 minutes | Direction: South              │
│                                                         │
│ Timeline Table:                                         │
│ ┌──────────┬─────────────────┬─────────────────────┐ │
│ │ AOS      │ 2025-10-05 ...  │ Rises above 10°     │ │
│ │ Maximum  │ 2025-10-05 ...  │ Peak at 75.3° @ 180°│ │
│ │ LOS      │ 2025-10-05 ...  │ Drops below 10°     │ │
│ └──────────┴─────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Cara Menggunakan

### 1. Input Data:
- Satellite Name: Nama satelit (contoh: ISS)
- TLE Line 1 & 2: Two-Line Element data
- Latitude & Longitude: Lokasi observer
- Elevation: Ketinggian lokasi (meter)
- Min Elevation: Minimum sudut di atas horizon (default 10°)

### 2. Klik "Calculate Passes"
- Sistem akan menghitung semua passes dalam 24 jam ke depan
- Hanya menampilkan passes di atas minimum elevation

### 3. Baca Hasil:
- **AOS Time**: Mulai mencari satelit di langit
- **Max Elevation Time**: Waktu terbaik untuk observasi
- **LOS Time**: Satelit sudah tidak terlihat

### 4. Export (Opsional):
- Klik "Export Data" untuk download CSV
- File berisi semua informasi passes
- Bisa dibuka di Excel untuk analisis lebih lanjut

## 📝 Contoh Interpretasi

### Pass dengan Max Elevation 75.3° @ 180° (South):
- **Kualitas**: Excellent (di atas 60°)
- **Visibility**: Hampir tepat di atas kepala
- **Arah**: Selatan (South)
- **Kapan mulai**: AOS time
- **Kapan terbaik**: Max elevation time
- **Kapan selesai**: LOS time

### Pass dengan Max Elevation 25.0° @ 45° (NE):
- **Kualitas**: Fair (20-30°)
- **Visibility**: Rendah, dekat horizon
- **Arah**: Timur Laut (Northeast)
- **Note**: Mungkin terhalang bangunan/pohon

## 🔧 Technical Details

### Backend (app.py):
- API endpoint: `/api/calculate-passes`
- Menggunakan Skyfield library
- Menghitung passes dengan `almanac.find_discrete()`
- Return format: JSON dengan arrays of passes

### Frontend (passing_time.html):
- AJAX call ke API
- Dynamic rendering dengan template literals
- CSV export dengan Blob API
- Real-time statistics calculation

## 🎨 Color Scheme (Fiery Ocean Theme)

- **AOS (Green)**: Success/Start event
- **Max Elevation (Yellow/Orange)**: Peak event
- **LOS (Red)**: End event
- **Cards**: Navy → Maroon gradient headers
- **Text**: High contrast untuk readability

## 📱 Responsive Design

- Mobile friendly dengan Bootstrap grid
- Card layout menyesuaikan di layar kecil
- Table scrollable di mobile
- Touch-friendly buttons

## 🚀 Performance

- Efficient calculation dengan step_days optimization
- Lazy loading untuk large datasets
- No unnecessary re-renders
- Fast CSV generation

## 📖 User Guide Summary

**Best Practices for Observation:**
1. Set up 5-10 minutes before AOS
2. Look in the azimuth direction
3. Track to maximum elevation
4. Higher elevation = better visibility

**Pass Quality:**
- 60°+ : Excellent - Overhead
- 45-60°: Very Good - High
- 30-45°: Good - Moderate
- 20-30°: Fair - Low
- <20°: Difficult - Near horizon
