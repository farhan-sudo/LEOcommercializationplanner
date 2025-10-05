"""
Test script untuk memastikan semua modul dapat diimport dengan benar
"""

import sys
import os

print("=" * 70)
print("Testing Satellite Tracking System Dependencies")
print("=" * 70)
print()

# Test imports
modules_to_test = [
    ("Flask", "flask"),
    ("NumPy", "numpy"),
    ("Matplotlib", "matplotlib"),
    ("Cartopy", "cartopy"),
    ("SGP4", "sgp4"),
    ("Skyfield", "skyfield"),
    ("PyProj", "pyproj"),
    ("Shapely", "shapely"),
]

failed_imports = []
success_count = 0

for name, module in modules_to_test:
    try:
        __import__(module)
        print(f"✓ {name:20} ... OK")
        success_count += 1
    except ImportError as e:
        print(f"✗ {name:20} ... FAILED")
        failed_imports.append((name, str(e)))

print()
print("=" * 70)
print(f"Results: {success_count}/{len(modules_to_test)} modules imported successfully")
print("=" * 70)

if failed_imports:
    print()
    print("Failed imports:")
    for name, error in failed_imports:
        print(f"  - {name}: {error}")
    print()
    print("Please install missing dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
else:
    print()
    print("✓ All dependencies are installed correctly!")
    print()
    
    # Test project modules
    print("=" * 70)
    print("Testing Project Modules")
    print("=" * 70)
    print()
    
    project_modules = [
        "collision_prediction",
        "debris",
    ]
    
    for module in project_modules:
        try:
            __import__(module)
            print(f"✓ {module:30} ... OK")
        except Exception as e:
            print(f"✗ {module:30} ... FAILED: {str(e)}")
    
    print()
    
    # Check for required files
    print("=" * 70)
    print("Checking Required Files")
    print("=" * 70)
    print()
    
    required_files = [
        "app.py",
        "collision_prediction.py",
        "debris.py",
        "FENGYUN debris.txt",
        "requirements.txt",
        "templates/base.html",
        "templates/index.html",
        "static/css/custom.css",
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file:40} ... EXISTS")
        else:
            print(f"✗ {file:40} ... MISSING")
            missing_files.append(file)
    
    print()
    print("=" * 70)
    
    if missing_files:
        print("Warning: Some files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        print()
    else:
        print("✓ All required files are present!")
    
    print()
    print("=" * 70)
    print("System is ready! Run 'python app.py' to start the server.")
    print("=" * 70)
    sys.exit(0)
