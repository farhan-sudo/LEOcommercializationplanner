"""
Test API endpoints untuk debris visualization
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 70)
print("Testing Debris Visualization API Endpoints")
print("=" * 70)
print()

# Test debris-data endpoint
print("1. Testing /api/debris-data")
print("-" * 70)

for category in [None, 0, 1, 2, 3, 4]:
    try:
        if category is None:
            url = f"{BASE_URL}/debris-data"
            print(f"   Testing: All categories")
        else:
            url = f"{BASE_URL}/debris-data?category={category}"
            print(f"   Testing: Category {category}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                count = data.get('count', 0)
                debris_len = len(data.get('debris', []))
                print(f"      ✓ Success: {count} total, {debris_len} returned")
            else:
                print(f"      ✗ Failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"      ✗ HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"      ✗ Connection error - Is Flask server running?")
        print()
        print("Please start the Flask server first:")
        print("  python app.py")
        exit(1)
    except Exception as e:
        print(f"      ✗ Error: {str(e)}")

print()
print("=" * 70)
print("Test Complete!")
print()
print("Note: Make sure Flask server is running on http://localhost:5000")
