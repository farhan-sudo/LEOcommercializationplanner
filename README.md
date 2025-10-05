# 🛰️ Satellite & Debris Tracking System

A comprehensive web application for tracking satellites, predicting collisions with space debris, and visualizing orbital data in real-time — powered by **Flask** as the backend.

---

## ✨ Features

### 1. 🚨 Collision Prediction
- Predict potential collisions between satellites and space debris  
- Uses **SGP4 orbital propagation**
- Configurable prediction periods and collision thresholds
- Detailed analysis of closest approaches

### 2. 🪐 Debris Visualization
- Interactive map visualization of space debris
- Categorized by altitude ranges (160–2000 km, LEO)
- Includes **FENGYUN-1C debris catalog** with 3,500+ tracked objects
- Both static and interactive **Leaflet** maps supported

### 3. 📡 Real-Time Satellite Tracking
- Track satellite positions in real-time
- Live map with auto-update capability
- ECI → Geodetic coordinate conversion
- Orbital period calculation

### 4. ⏱️ Satellite Passing Time Calculator
- Calculate when satellites pass over specific locations
- AOS (Acquisition of Signal) and LOS (Loss of Signal) times
- Maximum altitude and azimuth during passes
- 24-hour prediction window

---

## 🚀 Technologies Used

| Category | Tools & Libraries |
|-----------|------------------|
| **Backend** | Flask |
| **Orbital Mechanics** | SGP4, Skyfield |
| **Mapping** | Cartopy, Leaflet.js |
| **Visualization** | Matplotlib, Chart.js |
| **Frontend** | Bootstrap 5, Font Awesome |
| **Geospatial** | PyProj, Shapely |

---

## 📋 Prerequisites

- Python 3.8 or higher  
- `pip` (Python package manager)  
- Internet connection (for map tiles)

---

## 🔧 Installation

### 1. Clone or Navigate to Project Directory
```bash
cd c:\Users\farhan\Projects\websitespaceapps\appss
```

2. Create a Virtual Environment (Recommended)
```   
python -m venv venv
venv\Scripts\activate
```
3. Install Dependencies
```
pip install -r requirements.txt

pip install --upgrade pip
pip install cartopy --no-binary cartopy
```

▶️ Running the Application

1. Start the Flask Server
```
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```
2. Access the Web Interface
Open your browser and go to:
```
http://localhost:5000
```

