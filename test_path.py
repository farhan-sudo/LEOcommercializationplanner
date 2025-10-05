"""
Quick test untuk verify debris file path
"""
import os
import sys

# Add appss to path
sys.path.insert(0, r'c:\Users\farhan\Projects\websitespaceapps\appss')

from collision_prediction import parse_debris_tle

# Test dengan path yang berbeda
print("=" * 70)
print("Testing Debris File Path Resolution")
print("=" * 70)
print()

test_paths = [
    'FENGYUN debris.txt',  # Relative
    r'c:\Users\farhan\Projects\websitespaceapps\appss\FENGYUN debris.txt',  # Absolute
]

for path in test_paths:
    print(f"Testing path: {path}")
    print(f"  Exists: {os.path.exists(path)}")
    
    try:
        debris = parse_debris_tle(path, filter_category=1)
        print(f"  ✓ Parsed: {len(debris)} debris")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    print()

print("=" * 70)
print("Test Complete!")
