# 🕐 Passing Time - Start Time Input Feature

## ✨ New Feature: Custom Start Time for Pass Search

### 📋 What's New

Pengguna sekarang dapat menentukan **kapan mulai mencari satellite passes**, tidak hanya dari waktu sekarang!

### 🎯 Input Fields yang Ditambahkan:

#### 1. **Start Date** 📅
- **Type**: Date picker
- **Purpose**: Pilih tanggal untuk mulai pencarian
- **Format**: YYYY-MM-DD
- **Example**: 2025-10-05

#### 2. **Start Time (UTC)** ⏰
- **Type**: Time picker
- **Purpose**: Pilih jam untuk mulai pencarian
- **Timezone**: UTC (Universal Time Coordinated)
- **Format**: HH:MM (24-hour format)
- **Example**: 15:30

#### 3. **Search Duration** ⏳
- **Type**: Dropdown select
- **Purpose**: Berapa lama mencari passes dari start time
- **Options**:
  - 6 hours
  - 12 hours
  - 24 hours (1 day) - DEFAULT
  - 48 hours (2 days)
  - 72 hours (3 days)
  - 168 hours (7 days)

### 🔘 Tombol Baru:

**"Use Current Time"** button:
- Icon: 🔄 (sync)
- Function: Mengisi start date dan time dengan waktu UTC sekarang
- Berguna untuk quick search dari waktu sekarang

### 💡 Use Cases:

#### Use Case 1: Cari Pass Besok Pagi
```
Start Date: 2025-10-06
Start Time: 06:00 (UTC)
Duration: 12 hours
→ Mencari passes dari jam 6 pagi sampai 6 sore besok
```

#### Use Case 2: Cari Pass Minggu Depan
```
Start Date: 2025-10-12
Start Time: 00:00 (UTC)
Duration: 168 hours (7 days)
→ Mencari passes selama seminggu penuh
```

#### Use Case 3: Cari Pass Malam Ini
```
Start Date: 2025-10-05
Start Time: 20:00 (UTC)
Duration: 8 hours
→ Mencari passes malam ini (20:00-04:00)
```

### 🖥️ Frontend Changes:

#### HTML Template (`passing_time.html`):
```html
<!-- New Section: Search Time Window -->
<div class="alert alert-light border">
    <h6>Search Time Window</h6>
    <p>Specify when to start searching and how long...</p>
</div>

<div class="row">
    <!-- Start Date Input -->
    <input type="date" id="startDate" required>
    
    <!-- Start Time Input -->
    <input type="time" id="startTime" required>
    
    <!-- Duration Select -->
    <select id="searchDuration">
        <option value="24" selected>24 hours</option>
        ...
    </select>
</div>
```

#### JavaScript Functions:
```javascript
// Set current UTC time
function setCurrentTime() {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toISOString().split('T')[1].substring(0, 5);
    document.getElementById('startDate').value = dateStr;
    document.getElementById('startTime').value = timeStr;
}

// Send to API
body: JSON.stringify({
    ...
    start_date: startDate,
    start_time: startTime,
    search_duration: searchDuration
})
```

### 🔧 Backend Changes:

#### API Endpoint (`app.py`):
```python
@app.route('/api/calculate-passes', methods=['POST'])
def api_calculate_passes():
    # Get user input
    start_date = data.get('start_date', '')
    start_time = data.get('start_time', '')
    search_duration = float(data.get('search_duration', 24))
    
    # Parse or use current time
    if start_date and start_time:
        start_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    else:
        start_dt = datetime.utcnow()
    
    # Calculate end time
    end_dt = start_dt + timedelta(hours=search_duration)
```

### 📊 Display Updates:

#### Results Header:
```
┌─────────────────────────────────────────────────────┐
│ Upcoming Passes                                     │
├─────────────────────────────────────────────────────┤
│ Location: -6.2000°, 106.8167°                      │
│ Min Elevation: 10°                                  │
│                                                     │
│ Search Period:                                      │
│ From: 2025-10-05 15:30:00 UTC                      │
│ To:   2025-10-06 15:30:00 UTC (24 hours)           │
└─────────────────────────────────────────────────────┘
```

### 🎨 UI/UX Enhancements:

1. **Info Alert Box**: 
   - Explains what the fields are for
   - Mentions UTC timezone
   - Provides quick tips

2. **"Use Current Time" Button**:
   - Quick action untuk set ke waktu sekarang
   - Auto-fills both date and time
   - Blue color (info style)

3. **Duration Dropdown**:
   - Clear labels with hours and days
   - Default 24 hours selected
   - Up to 7 days option

4. **Validation**:
   - Required fields enforced
   - Date/time format validated by HTML5
   - Error messages if fields empty

### ⚠️ Important Notes:

#### Timezone: UTC Only
```
⚠️ All times are in UTC timezone!

Jakarta (WIB):  UTC +7
New York (EST): UTC -5
London (GMT):   UTC +0
Tokyo (JST):    UTC +9

Example: 
- Jakarta 10:00 AM = 03:00 UTC
- Convert your local time to UTC before input
```

#### Search Duration Limits:
- **Minimum**: 1 hour (not in dropdown, but API supports)
- **Maximum**: 7 days (168 hours)
- **Recommended**: 24-48 hours for best performance

#### TLE Accuracy:
```
⚠️ TLE data has limited validity period
- Accurate for ±3-7 days from epoch
- For long duration (7 days), get fresh TLE
- Check NORAD catalog for updated TLE
```

### 📝 Example Workflow:

```
1. User fills satellite TLE data
2. User fills location (lat, lon, elevation)
3. User clicks "Use Current Time" 
   → Auto-fills current UTC time
4. User selects "48 hours" duration
5. User clicks "Calculate Passes"
6. System searches passes from now until 48 hours ahead
7. Results show all passes in that 48-hour window
```

### 🔍 Search Algorithm:

```python
# Pseudo-code
start = user_input_datetime  # or current_time if not provided
end = start + duration_hours

for each_pass in satellite_orbit:
    if pass.aos_time >= start and pass.aos_time <= end:
        if pass.max_elevation >= min_elevation:
            include_in_results(pass)
```

### 📈 Benefits:

1. **Planning Ahead**: 
   - Schedule observations days in advance
   - Plan around weather forecasts
   - Coordinate with team members

2. **Flexibility**:
   - Search any time period, not just "from now"
   - Compare passes at different times
   - Find optimal observation windows

3. **Historical Analysis** (future feature):
   - Could be extended to search past passes
   - Useful for verification and debugging

4. **Event Coordination**:
   - Find passes during specific events
   - Match with launch windows
   - Coordinate multiple ground stations

### 🚀 Future Enhancements (Ideas):

- [ ] Timezone selector (auto-convert to UTC)
- [ ] "Quick Select" presets (Tonight, Tomorrow, This Weekend)
- [ ] Calendar view of passes
- [ ] Email/SMS alerts for upcoming passes
- [ ] Save favorite search configurations
- [ ] Export to Google Calendar
- [ ] Multiple satellite comparison

### 📖 User Guide:

**How to Use:**
1. Enter satellite TLE data
2. Enter your location coordinates
3. **NEW**: Choose start date and time (UTC)
4. **NEW**: Choose search duration (6-168 hours)
5. Click "Calculate Passes"
6. View all passes in your selected time window

**Tips:**
- Click "Use Current Time" for searching from now
- Use longer durations (48-72 hours) for better planning
- Remember to convert your local time to UTC
- Check TLE epoch date - should be recent (within 1 week)
