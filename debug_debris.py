"""
Debug script to check debris altitude distribution
"""
from collision_prediction import parse_debris_tle, categorize_altitude
from collections import defaultdict

print("=" * 70)
print("FENGYUN Debris Altitude Distribution Analysis")
print("=" * 70)
print()

# Parse all debris
debris_list = parse_debris_tle('FENGYUN debris.txt', filter_category=None)

print(f"Total debris parsed: {len(debris_list)}")
print()

if len(debris_list) == 0:
    print("ERROR: No debris parsed! Check FENGYUN debris.txt file.")
    exit(1)

# Count by category
category_count = defaultdict(int)
category_names = {
    0: '160-528 km',
    1: '528-896 km',
    2: '896-1264 km',
    3: '1264-1632 km',
    4: '1632-2000 km',
    -1: 'Out of range'
}

for debris in debris_list:
    cat_idx = debris['cat_idx']
    category_count[cat_idx] += 1

print("Distribution by Category:")
print("-" * 70)
for cat_idx in sorted(category_count.keys()):
    count = category_count[cat_idx]
    name = category_names.get(cat_idx, 'Unknown')
    percentage = (count / len(debris_list)) * 100
    print(f"  Category {cat_idx:2} ({name:20}): {count:5} debris ({percentage:5.1f}%)")

print()

# Show altitude statistics
altitudes = [d['alt'] for d in debris_list]
print("Altitude Statistics:")
print("-" * 70)
print(f"  Minimum altitude: {min(altitudes):.2f} km")
print(f"  Maximum altitude: {max(altitudes):.2f} km")
print(f"  Average altitude: {sum(altitudes)/len(altitudes):.2f} km")
print()

# Show sample debris from each category
print("Sample Debris from Each Category:")
print("-" * 70)
samples_shown = defaultdict(int)
for debris in debris_list:
    cat_idx = debris['cat_idx']
    if samples_shown[cat_idx] < 2 and cat_idx >= 0:  # Show 2 samples per category
        print(f"  Cat {cat_idx}: Alt={debris['alt']:.2f} km, Lat={debris['lat']:.2f}°, Lon={debris['lon']:.2f}°")
        samples_shown[cat_idx] += 1

print()
print("=" * 70)

# Test filtering
print("Testing Category Filtering:")
print("-" * 70)
for cat in range(5):
    filtered = parse_debris_tle('FENGYUN debris.txt', filter_category=cat)
    print(f"  Category {cat} ({category_names[cat]:20}): {len(filtered)} debris")

print()
print("=" * 70)
print("Analysis Complete!")
