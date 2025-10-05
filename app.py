from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
from datetime import datetime, timedelta
import io
import base64
import os
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend untuk Flask
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from collision_prediction import (
    predict_satellite_collision,
    propagate_satellite_trajectory,
    parse_debris_tle,
    calculate_orbital_period,
    categorize_altitude,
    eci_to_latlon
)
from sgp4.api import Satrec, jday
from skyfield.api import load, EarthSatellite, wgs84
from skyfield import almanac
from config import config

# Configuration for Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
app = Flask(__name__, 
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Konfigurasi - Use absolute path for debris file
DEBRIS_FILE = os.path.join(BASE_DIR, app.config['DEBRIS_FILE'])

# Verify debris file exists
if not os.path.exists(DEBRIS_FILE):
    print(f"WARNING: Debris file not found at {DEBRIS_FILE}")
    print("Please ensure FENGYUN debris.txt is in the same directory as app.py")

@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/dashboard')
def index():
    """Dashboard utama"""
    return render_template('index.html')

@app.route('/test-icons')
def test_icons():
    """Test page untuk melihat apakah ikon berfungsi"""
    return render_template('test_icons.html')

@app.route('/collision-prediction')
def collision_prediction_page():
    """Halaman Collision Prediction"""
    return render_template('collision_prediction.html')

@app.route('/debris-visualization')
def debris_visualization_page():
    """Halaman Debris Visualization"""
    return render_template('debris_visualization.html')

@app.route('/satellite-tracking')
def satellite_tracking_page():
    """Halaman Satellite Tracking"""
    return render_template('satellite_tracking.html')

@app.route('/passing-time')
def passing_time_page():
    """Halaman Satellite Passing Time"""
    return render_template('passing_time.html')

# ========== API ENDPOINTS ==========

@app.route('/api/predict-collision', methods=['POST'])
def api_predict_collision():
    """API untuk prediksi collision"""
    try:
        data = request.json
        tle_line1 = data.get('tle_line1', '').strip()
        tle_line2 = data.get('tle_line2', '').strip()
        num_periods = int(data.get('num_periods', 5))
        time_step = int(data.get('time_step', 1))
        threshold = float(data.get('threshold', 5.0))
        
        if not tle_line1 or not tle_line2:
            return jsonify({'error': 'TLE lines required'}), 400
        
        result = predict_satellite_collision(
            tle_line1, tle_line2, DEBRIS_FILE,
            num_periods=num_periods,
            time_step_minutes=time_step,
            threshold=threshold
        )
        
        # Convert datetime objects to strings
        if result['closest_sat_point']:
            result['closest_sat_point']['time'] = result['closest_sat_point']['time'].strftime('%Y-%m-%d %H:%M:%S')
        
        for cp in result['collision_points']:
            cp['time'] = cp['time'].strftime('%Y-%m-%d %H:%M:%S')
            cp['sat_pos']['time'] = cp['sat_pos']['time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'collision': result['collision'],
            'collision_count': result['collision_count'],
            'min_distance': result['min_distance'],
            'closest_point': result['closest_sat_point'],
            'collision_points': result['collision_points'][:10]  # Limit to 10 points
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debris-data', methods=['GET'])
def api_debris_data():
    """API untuk mendapatkan data debris"""
    try:
        category = request.args.get('category', None)
        if category is not None and category != '':
            category = int(category)
        else:
            category = None
        
        debris_positions = parse_debris_tle(DEBRIS_FILE, filter_category=category)
        
        # Format data untuk frontend
        debris_list = []
        for debris in debris_positions[:1000]:  # Limit to 1000 for performance
            debris_list.append({
                'lat': float(debris['lat']),
                'lon': float(debris['lon']),
                'alt': float(debris['alt']),
                'category': debris['category']
            })
        
        return jsonify({
            'success': True,
            'count': len(debris_positions),
            'debris': debris_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debris-map', methods=['GET'])
def api_debris_map():
    """API untuk generate debris map sebagai image"""
    try:
        category = request.args.get('category', None)
        if category is not None and category != '':
            category = int(category)
        else:
            category = None
        
        debris_positions = parse_debris_tle(DEBRIS_FILE, filter_category=category)
        
        # Create map
        fig = plt.figure(figsize=(14, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, 
                     linewidth=0.5, alpha=0.5)
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
        
        if debris_positions:
            lats = [d['lat'] for d in debris_positions]
            lons = [d['lon'] for d in debris_positions]
            alts = [d['alt'] for d in debris_positions]
            
            scatter = ax.scatter(lons, lats, c=alts, s=15, alpha=0.6,
                               cmap='jet', transform=ccrs.PlateCarree())
            
            cbar = plt.colorbar(scatter, ax=ax, orientation='horizontal',
                               pad=0.05, shrink=0.7)
            cbar.set_label('Debris Altitude (km)', fontsize=10)
        
        category_name = f"Category {category}" if category is not None else "All Categories"
        plt.title(f'Debris Distribution - {category_name}\nTotal: {len(debris_positions)} debris',
                 fontsize=14, fontweight='bold')
        
        # Save to bytes
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=100, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64
        img_base64 = base64.b64encode(img_bytes.read()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'count': len(debris_positions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/satellite-position', methods=['POST'])
def api_satellite_position():
    """API untuk mendapatkan posisi satelit"""
    try:
        data = request.json
        tle_line1 = data.get('tle_line1', '').strip()
        tle_line2 = data.get('tle_line2', '').strip()
        
        if not tle_line1 or not tle_line2:
            return jsonify({'error': 'TLE lines required'}), 400
        
        # Parse TLE
        satellite = Satrec.twoline2rv(tle_line1, tle_line2)
        
        # Current time
        current_time = datetime.utcnow()
        jd, fr = jday(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second)
        
        # Propagate
        error, position, velocity = satellite.sgp4(jd, fr)
        
        if error != 0:
            return jsonify({'error': 'SGP4 propagation error'}), 500
        
        x, y, z = position
        lat, lon, alt = eci_to_latlon(x, y, z)
        
        # Calculate orbital period
        period = calculate_orbital_period(tle_line1, tle_line2)
        
        return jsonify({
            'success': True,
            'position': {
                'lat': lat,
                'lon': lon,
                'alt': alt,
                'x': x,
                'y': y,
                'z': z
            },
            'orbital_period': period,
            'time': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate-passes', methods=['POST'])
def api_calculate_passes():
    """API untuk menghitung passing time satelit"""
    try:
        data = request.json
        tle_name = data.get('tle_name', 'SATELLITE')
        tle_line1 = data.get('tle_line1', '').strip()
        tle_line2 = data.get('tle_line2', '').strip()
        latitude = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
        elevation = float(data.get('elevation', 0))
        min_elevation = float(data.get('min_elevation', 10))
        
        # Get start time from user input or use current time
        start_date = data.get('start_date', '')
        start_time = data.get('start_time', '')
        search_duration = float(data.get('search_duration', 24))  # hours
        
        if not tle_line1 or not tle_line2:
            return jsonify({'error': 'TLE lines required'}), 400
        
        # Setup Skyfield
        ts = load.timescale()
        satellite = EarthSatellite(tle_line1, tle_line2, tle_name, ts)
        observer_topos = wgs84.latlon(
            latitude_degrees=latitude,
            longitude_degrees=longitude,
            elevation_m=elevation
        )
        
        # Time window: use user-specified time or current time
        if start_date and start_time:
            # Parse user input (format: YYYY-MM-DD and HH:MM)
            start_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        else:
            start_dt = datetime.utcnow()
        
        end_dt = start_dt + timedelta(hours=search_duration)
        
        start_time = ts.utc(start_dt.year, start_dt.month, start_dt.day, 
                           start_dt.hour, start_dt.minute, start_dt.second)
        end_time = ts.utc(end_dt.year, end_dt.month, end_dt.day,
                         end_dt.hour, end_dt.minute, end_dt.second)
        
        # Calculate orbital period for step size
        mean_motion_rad_per_min = satellite.model.nm
        orbital_period_minutes = (2 * np.pi) / mean_motion_rad_per_min
        orbital_period_days = orbital_period_minutes / (24 * 60)
        step_days = orbital_period_days / 20.0
        
        def is_satellite_above_horizon(t):
            difference = satellite - observer_topos
            alt, _, _ = difference.at(t).altaz()
            return (alt.degrees >= min_elevation).astype(int)
        
        is_satellite_above_horizon.step_days = step_days
        
        # Find passes
        times, events = almanac.find_discrete(start_time, end_time, is_satellite_above_horizon)
        
        # Process results
        passes = []
        i = 0
        
        if len(events) > 0 and events[0] == 0:
            i = 1
        
        while i < len(events) - 1:
            if events[i] == 1:
                aos_time = times[i]
                
                if i + 1 < len(events) and events[i + 1] == 0:
                    los_time = times[i + 1]
                    
                    # Find max altitude
                    t_sample = ts.linspace(aos_time, los_time, 20)
                    alt, az, _ = (satellite - observer_topos).at(t_sample).altaz()
                    
                    max_alt_index = np.argmax(alt.degrees)
                    max_alt_time = t_sample[max_alt_index]
                    max_alt_deg = alt.degrees[max_alt_index]
                    max_az_deg = az.degrees[max_alt_index]
                    
                    # Calculate duration
                    pass_duration = (los_time.tt - aos_time.tt) * 24 * 60
                    
                    passes.append({
                        'aos_time': aos_time.utc_strftime('%Y-%m-%d %H:%M:%S UTC'),
                        'los_time': los_time.utc_strftime('%Y-%m-%d %H:%M:%S UTC'),
                        'max_alt_time': max_alt_time.utc_strftime('%H:%M:%S UTC'),
                        'max_alt_degrees': f'{max_alt_deg:.2f}',
                        'max_azimuth_degrees': f'{max_az_deg:.2f}',
                        'duration_minutes': f'{pass_duration:.2f}'
                    })
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        return jsonify({
            'success': True,
            'passes': passes,
            'count': len(passes)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)  # Set to False for production
