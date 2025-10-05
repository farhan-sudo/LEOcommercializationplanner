import re
import os

# Template files to process
template_files = [
    'appss/templates/index.html',
    'appss/templates/collision_prediction.html',
    'appss/templates/debris_visualization.html',
    'appss/templates/satellite_tracking.html',
    'appss/templates/passing_time.html'
]

# Pattern to match Font Awesome icons
pattern = r'<i class="fa[^"]*"[^>]*></i>\s*'

for file_path in template_files:
    if os.path.exists(file_path):
        print(f"Processing {file_path}...")
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count matches
        matches = re.findall(pattern, content)
        print(f"  Found {len(matches)} icons")
        
        # Remove icons
        content = re.sub(pattern, '', content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Removed all icons from {file_path}")
    else:
        print(f"  ✗ File not found: {file_path}")

print("\nDone! All icons removed.")
