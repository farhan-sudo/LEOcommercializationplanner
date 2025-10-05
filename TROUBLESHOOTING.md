# 🐛 Troubleshooting Guide - Debris Visualization

## ✅ Problem SOLVED: Debris tidak muncul di kategori

### Masalah
Ketika mengakses halaman "Debris Visualization" dan memilih kategori, debris tidak muncul atau count menunjukkan 0.

### Penyebab
File `FENGYUN debris.txt` tidak ditemukan karena Flask mencari dengan **relative path** dari directory tempat server dijalankan, bukan dari directory file `app.py`.

### Solusi
✅ **SUDAH DIPERBAIKI** - File `app.py` sekarang menggunakan **absolute path** berdasarkan lokasi script:

```python
# Di app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBRIS_FILE = os.path.join(BASE_DIR, app.config['DEBRIS_FILE'])
```

### Verifikasi Perbaikan

#### 1. Check File Exists
```python
python debug_debris.py
```

Output yang benar:
```
Total debris parsed: 1885
Distribution by Category:
  Category  0 (160-528 km          ):    41 debris (  2.2%)
  Category  1 (528-896 km          ):  1385 debris ( 73.5%)
  Category  2 (896-1264 km         ):   422 debris ( 22.4%)
  Category  3 (1264-1632 km        ):    29 debris (  1.5%)
  Category  4 (1632-2000 km        ):     2 debris (  0.1%)
```

#### 2. Start Flask Server
```cmd
python app.py
```

Saat startup, seharusnya **TIDAK** ada warning tentang debris file.

#### 3. Test di Browser
1. Buka http://localhost:5000/debris-visualization
2. Pilih **Category 1 (528-896 km)** - kategori dengan debris terbanyak
3. Klik "Generate Map"
4. Seharusnya muncul:
   - Total Debris Objects: **1,385**
   - Altitude Range: **528-896 km**
   - Debris map image
   - Interactive Leaflet map

#### 4. Test Semua Kategori

| Kategori | Altitude Range | Expected Count |
|----------|----------------|----------------|
| 0        | 160-528 km     | 41 debris      |
| 1        | 528-896 km     | **1,385 debris** |
| 2        | 896-1264 km    | 422 debris     |
| 3        | 1264-1632 km   | 29 debris      |
| 4        | 1632-2000 km   | 2 debris       |

### Catatan Penting

1. **Kategori dengan Data Terbanyak**
   - **Kategori 1 (528-896 km)**: 1,385 debris (73.5%)
   - Gunakan ini untuk testing awal

2. **Kategori dengan Data Paling Sedikit**
   - **Kategori 4 (1632-2000 km)**: 2 debris (0.1%)
   - Wajar jika map terlihat kosong

3. **File Path Requirements**
   - `FENGYUN debris.txt` harus ada di folder `appss/`
   - Path dihandle otomatis oleh `app.py`
   - Tidak perlu setting environment variable

### Error Messages

#### ❌ "Error: File FENGYUN debris.txt tidak ditemukan"
**Penyebab**: File path salah atau file tidak ada  
**Solusi**: 
1. Cek file exists: `dir "FENGYUN debris.txt"` (dari folder appss)
2. Pastikan menjalankan dari directory yang benar
3. Gunakan absolute path di app.py (sudah diperbaiki)

#### ❌ "Error: invalid literal for int() with base 10: ''"
**Penyebab**: Empty string dari form select tidak di-handle  
**Solusi**: Sudah diperbaiki di API endpoint dengan check `if category != ''`

#### ❌ Count: 0 di semua kategori
**Penyebab**: 
- File tidak terparsing dengan benar
- Filter category salah
- TLE data corrupt

**Solusi**:
```bash
# Run debug script
python debug_debris.py

# Check output - jika 0, berarti file bermasalah
# Re-download FENGYUN debris.txt dari sumber yang valid
```

### Testing Commands

```bash
# 1. Change to project directory
cd c:\Users\farhan\Projects\websitespaceapps\appss

# 2. Test debris parsing
python debug_debris.py

# 3. Start Flask server
python app.py

# 4. Open browser
start http://localhost:5000/debris-visualization
```

### Browser Console Check

Buka Developer Tools (F12) > Console. Periksa error JavaScript:

#### ✅ Success Response:
```json
{
  "success": true,
  "count": 1385,
  "debris": [{...}, {...}, ...]
}
```

#### ❌ Error Response:
```json
{
  "error": "Error message here"
}
```

### API Endpoint Testing

Gunakan browser atau curl:

```bash
# Test debris-data API
curl "http://localhost:5000/api/debris-data?category=1"

# Expected: JSON dengan count: 1385

# Test debris-map API
curl "http://localhost:5000/api/debris-map?category=1"

# Expected: JSON dengan image base64
```

### Performance Notes

- **Category 1 (1,385 debris)**: Map generation ~5-10 detik
- **Category 4 (2 debris)**: Map generation ~1-2 detik
- Interactive map dibatasi 500 markers untuk performa

### Known Issues & Workarounds

1. **Cartopy Installation Error (Windows)**
   - Download pre-built wheel dari https://www.lfd.uci.edu/~gohlke/pythonlibs/
   - Install: `pip install Cartopy‑0.22.0‑cp312‑cp312‑win_amd64.whl`

2. **Map Tiles Tidak Load**
   - Cek koneksi internet
   - OpenStreetMap tiles butuh internet
   - Clear browser cache

3. **Slow Map Generation**
   - Normal untuk kategori dengan banyak debris
   - Loading overlay akan muncul
   - Tunggu hingga selesai (jangan refresh)

---

## 📊 Expected Behavior Summary

### Kategori 0 (160-528 km)
- Count: 41 debris
- Map: Sparse, beberapa titik tersebar
- Load time: Fast (~2-3 detik)

### Kategori 1 (528-896 km) ⭐ RECOMMENDED untuk testing
- Count: 1,385 debris
- Map: Dense, banyak titik
- Load time: Medium (~5-10 detik)

### Kategori 2 (896-1264 km)
- Count: 422 debris
- Map: Moderate density
- Load time: Medium (~3-5 detik)

### Kategori 3 (1264-1632 km)
- Count: 29 debris
- Map: Sparse
- Load time: Fast (~2 detik)

### Kategori 4 (1632-2000 km)
- Count: 2 debris
- Map: Very sparse (hampir kosong)
- Load time: Very fast (~1 detik)

---

**Status**: ✅ **FIXED** - Oktober 5, 2025  
**Last Updated**: Oktober 5, 2025
