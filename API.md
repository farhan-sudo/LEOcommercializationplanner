# 📡 API Documentation

Complete API reference for the Satellite & Debris Tracking System.

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### 1. Predict Collision

Predict potential collisions between a satellite and space debris.

**Endpoint:** `POST /api/predict-collision`

**Request Body:**
```json
{
  "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
  "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172",
  "num_periods": 5,
  "time_step": 1,
  "threshold": 5.0
}
```

**Parameters:**
- `tle_line1` (string, required): First line of TLE data
- `tle_line2` (string, required): Second line of TLE data
- `num_periods` (integer, optional): Number of orbital periods to predict (default: 5)
- `time_step` (integer, optional): Time step in minutes (default: 1)
- `threshold` (float, optional): Collision threshold in km (default: 5.0)

**Response:**
```json
{
  "success": true,
  "collision": false,
  "collision_count": 0,
  "min_distance": 125.45,
  "closest_point": {
    "time": "2025-10-05 14:23:45",
    "lat": -23.45,
    "lon": 145.67,
    "alt": 415.23,
    "x": 3456.78,
    "y": -2345.67,
    "z": 5678.90
  },
  "collision_points": []
}
```

**Example (Python):**
```python
import requests

url = "http://localhost:5000/api/predict-collision"
data = {
    "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
    "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172",
    "num_periods": 5,
    "time_step": 1,
    "threshold": 5.0
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

---

### 2. Get Debris Data

Retrieve debris positions filtered by altitude category.

**Endpoint:** `GET /api/debris-data`

**Query Parameters:**
- `category` (integer, optional): Altitude category (0-4)
  - 0: 160-528 km
  - 1: 528-896 km
  - 2: 896-1264 km
  - 3: 1264-1632 km
  - 4: 1632-2000 km
  - (omit for all categories)

**Response:**
```json
{
  "success": true,
  "count": 3547,
  "debris": [
    {
      "lat": 45.23,
      "lon": -123.45,
      "alt": 678.90,
      "category": "528-896 km"
    },
    ...
  ]
}
```

**Example (cURL):**
```bash
curl "http://localhost:5000/api/debris-data?category=1"
```

**Example (JavaScript):**
```javascript
fetch('http://localhost:5000/api/debris-data?category=1')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

### 3. Generate Debris Map

Generate a map visualization of debris distribution.

**Endpoint:** `GET /api/debris-map`

**Query Parameters:**
- `category` (integer, optional): Altitude category (0-4)

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "count": 3547
}
```

**Example (Python):**
```python
import requests
import base64
from PIL import Image
from io import BytesIO

url = "http://localhost:5000/api/debris-map?category=2"
response = requests.get(url)
data = response.json()

# Decode base64 image
image_data = data['image'].split(',')[1]
image = Image.open(BytesIO(base64.b64decode(image_data)))
image.show()
```

---

### 4. Get Satellite Position

Get current position of a satellite.

**Endpoint:** `POST /api/satellite-position`

**Request Body:**
```json
{
  "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
  "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172"
}
```

**Response:**
```json
{
  "success": true,
  "position": {
    "lat": -23.45,
    "lon": 145.67,
    "alt": 415.23,
    "x": 3456.78,
    "y": -2345.67,
    "z": 5678.90
  },
  "orbital_period": 92.68,
  "time": "2025-10-05 14:23:45"
}
```

**Example (JavaScript - Fetch):**
```javascript
async function getSatellitePosition() {
  const response = await fetch('http://localhost:5000/api/satellite-position', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      tle_line1: "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
      tle_line2: "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172"
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

---

### 5. Calculate Satellite Passes

Calculate when a satellite passes over a specific location.

**Endpoint:** `POST /api/calculate-passes`

**Request Body:**
```json
{
  "tle_name": "ISS (ZARYA)",
  "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
  "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172",
  "latitude": -6.200000,
  "longitude": 106.816666,
  "elevation": 5,
  "min_elevation": 10
}
```

**Parameters:**
- `tle_name` (string, required): Satellite name
- `tle_line1` (string, required): First line of TLE
- `tle_line2` (string, required): Second line of TLE
- `latitude` (float, required): Observer latitude in degrees
- `longitude` (float, required): Observer longitude in degrees
- `elevation` (float, required): Observer elevation in meters
- `min_elevation` (float, required): Minimum elevation angle in degrees

**Response:**
```json
{
  "success": true,
  "passes": [
    {
      "aos_time": "2025-10-05 15:30:00 UTC",
      "los_time": "2025-10-05 15:37:00 UTC",
      "max_alt_time": "15:33:30 UTC",
      "max_alt_degrees": "45.23",
      "max_azimuth_degrees": "180.45",
      "duration_minutes": "7.00"
    },
    ...
  ],
  "count": 5
}
```

**Example (Python):**
```python
import requests

url = "http://localhost:5000/api/calculate-passes"
data = {
    "tle_name": "ISS (ZARYA)",
    "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
    "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172",
    "latitude": -6.200000,
    "longitude": 106.816666,
    "elevation": 5,
    "min_elevation": 10
}

response = requests.post(url, json=data)
result = response.json()

for i, pass_info in enumerate(result['passes'], 1):
    print(f"Pass #{i}:")
    print(f"  AOS: {pass_info['aos_time']}")
    print(f"  LOS: {pass_info['los_time']}")
    print(f"  Max Alt: {pass_info['max_alt_degrees']}°")
    print(f"  Duration: {pass_info['duration_minutes']} min")
    print()
```

---

## Error Handling

All endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `500`: Internal Server Error

**Example Error Response:**
```json
{
  "error": "TLE lines required"
}
```

---

## Rate Limiting

Currently, there are no rate limits. However, for production use, consider:
- Maximum 100 requests per minute per IP
- Maximum 1000 requests per hour per IP

---

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins in development mode.

For production, configure specific origins in `app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

---

## Authentication

Currently, no authentication is required. For production deployment, consider adding:
- API keys
- JWT tokens
- OAuth 2.0

---

## Examples in Different Languages

### Python
```python
import requests

class SatelliteAPI:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
    
    def predict_collision(self, tle1, tle2, **kwargs):
        url = f"{self.base_url}/predict-collision"
        data = {"tle_line1": tle1, "tle_line2": tle2, **kwargs}
        return requests.post(url, json=data).json()
    
    def get_debris(self, category=None):
        url = f"{self.base_url}/debris-data"
        params = {"category": category} if category else {}
        return requests.get(url, params=params).json()

# Usage
api = SatelliteAPI()
result = api.predict_collision(
    "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
    "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172"
)
print(result)
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

class SatelliteAPI {
  constructor(baseURL = 'http://localhost:5000/api') {
    this.baseURL = baseURL;
  }
  
  async predictCollision(tle1, tle2, options = {}) {
    const response = await axios.post(`${this.baseURL}/predict-collision`, {
      tle_line1: tle1,
      tle_line2: tle2,
      ...options
    });
    return response.data;
  }
  
  async getDebris(category = null) {
    const params = category !== null ? { category } : {};
    const response = await axios.get(`${this.baseURL}/debris-data`, { params });
    return response.data;
  }
}

// Usage
const api = new SatelliteAPI();
api.predictCollision(
  "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
  "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172"
).then(result => console.log(result));
```

### cURL
```bash
# Predict collision
curl -X POST http://localhost:5000/api/predict-collision \
  -H "Content-Type: application/json" \
  -d '{
    "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
    "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172",
    "num_periods": 5,
    "time_step": 1,
    "threshold": 5.0
  }'

# Get debris data
curl "http://localhost:5000/api/debris-data?category=1"

# Get satellite position
curl -X POST http://localhost:5000/api/satellite-position \
  -H "Content-Type: application/json" \
  -d '{
    "tle_line1": "1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997",
    "tle_line2": "2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172"
  }'
```

---

## Best Practices

1. **Cache TLE Data**: TLE data doesn't change frequently. Cache it for at least 1 hour.
2. **Use Appropriate Time Steps**: Smaller time steps (1-2 min) for accuracy, larger (5-10 min) for speed.
3. **Filter Debris by Category**: Loading all debris can be slow. Filter by relevant altitude category.
4. **Handle Errors Gracefully**: Always check the `success` field and handle errors appropriately.
5. **Update TLE Regularly**: Get fresh TLE data daily from CelesTrak or Space-Track.

---

## Testing

Use tools like Postman, Insomnia, or curl to test the API endpoints.

**Postman Collection:** (Create a collection with all endpoints for easy testing)

---

## Support

For API issues or questions, please refer to the main README.md or open an issue in the project repository.

---

**Last Updated:** October 5, 2025
