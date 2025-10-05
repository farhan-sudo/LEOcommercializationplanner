from skyfield.api import load, EarthSatellite, wgs84
from skyfield import almanac
import numpy as np
import datetime as dt

def calculate_satellite_passes(TLE, observer_datetime, observer_position, min_elevation_degrees=10):
    ts = load.timescale()
    
    # satellite
    name, line1, line2 = TLE
    satellite = EarthSatellite(line1, line2, name, ts)

    # Define ground observer position
    latitude, longitude, elevation_m = observer_position
    observer_topos = wgs84.latlon(
        latitude_degrees=latitude,
        longitude_degrees=longitude,
        elevation_m=elevation_m
    )

    # Define time window: Start and End
    YYYY, MM, DD, H, M, S = observer_datetime
    start_dt = dt.datetime(YYYY, MM, DD, H, M, S)
    end_dt = start_dt + dt.timedelta(days=1) # Search for 24 hours
    
    start_time = ts.utc(start_dt.year, start_dt.month, start_dt.day, start_dt.hour, start_dt.minute, start_dt.second)
    end_time = ts.utc(end_dt.year, end_dt.month, end_dt.day, end_dt.hour, end_dt.minute, end_dt.second)

    # Calculate approximate orbital period (in days) to determine step_days
    mean_motion_rad_per_min = satellite.model.nm # rad per min
    orbital_period_minutes = (2 * np.pi) / mean_motion_rad_per_min
    orbital_period_days = orbital_period_minutes / (24 * 60)
    STEP_DAYS = orbital_period_days / 20.0

    def is_satellite_above_horizon(t):
        # Returns 1 if the satellite is above the minimum elevation, 0 otherwise.

        difference = satellite - observer_topos
        alt, _, _ = difference.at(t).altaz()
        
        return (alt.degrees >= min_elevation_degrees).astype(int)
    
    is_satellite_above_horizon.step_days = STEP_DAYS

    # Find Passes (AOS and LOS)
    times, events = almanac.find_discrete(start_time, end_time, is_satellite_above_horizon)
    
    # Process results
    passes = []

    # Check the satellite state at the very start time.
    is_up_at_start = is_satellite_above_horizon(start_time).item()

    # Events come in pairs: 0=LOS (set), 1=AOS (rise).
    i = 0

    if len(events) > 0:
        # If the first event is LOS (0), it means the pass started before the window (if up)
        # or it's a false event (if down). Skip it to start at a proper AOS event.
        if events[0] == 0:
            i = 1


    while i < len(events) - 1:
        # We expect a transition from 0 (down) to 1 (up) for AOS
        if events[i] == 1:
            aos_time = times[i]
            
            # The next event must be LOS (0)
            if i + 1 < len(events) and events[i + 1] == 0:
                los_time = times[i + 1]

                # Find Max Altitude within the Pass
                t_sample = ts.linspace(aos_time, los_time, 20)
                alt, _, _ = (satellite - observer_topos).at(t_sample).altaz()
                
                max_alt_index = np.argmax(alt.degrees)
                max_alt_time = t_sample[max_alt_index]
                max_alt_deg = alt.degrees[max_alt_index]

                # Calculate duration
                pass_duration = (los_time.tt - aos_time.tt) * 24 * 60

                passes.append({
                    'AOS_time': aos_time.utc_strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'LOS_time': los_time.utc_strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'Max_Alt_time': max_alt_time.utc_strftime('%H:%M:%S UTC'),
                    'Max_Alt_degrees': f'{max_alt_deg:.2f}',
                    'Duration_minutes': f'{pass_duration:.2f}'
                })
                i += 2 # Move to the next potential AOS event
            else:
                i += 1
        else:
            i += 1

    return passes



# TLE for ISS (Replace with your satellite)
ISS_TLE = (
    "ISS (ZARYA)",             
"1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
"2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172"
)

# Makassar, Indonesia coordinates (Approx. -5.16° Latitude, 119.44° Longitude, 5m Elevation)
MAKASSAR_POS = (-6.200000, 106.816666, 5)

# Starting time for search: Current time is 2025-10-05 1:25 PM WIB (06:25 UTC)
START_TIME_TUPLE = (2025, 10, 8, 1, 5, 5)

# Minimum elevation (horizon) for "visibility"
MIN_ELEVATION = 10 

passes = calculate_satellite_passes(
    ISS_TLE, 
    START_TIME_TUPLE, 
    MAKASSAR_POS, 
    MIN_ELEVATION
)

print(f"\n--- Satellite Passes over Makassar (Min Alt: {MIN_ELEVATION}° - 24 Hours) ---")
if not passes:
    print("No passes found above the minimum elevation in the next 24 hours.")
else:
    for pass_info in passes:
        print(f"AOS: {pass_info['AOS_time']} | LOS: {pass_info['LOS_time']} | Max Alt: {pass_info['Max_Alt_degrees']}° at {pass_info['Max_Alt_time']} | Duration: {pass_info['Duration_minutes']} min")