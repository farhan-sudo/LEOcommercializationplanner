/**
 * Debris Visualization Page JavaScript
 */

let leafletMapInstance = null;

const categoryNames = {
    '0': '160-528 km',
    '1': '528-896 km',
    '2': '896-1264 km',
    '3': '1264-1632 km',
    '4': '1632-2000 km',
    '': 'All Categories'
};

async function loadDebrisMap() {
    const category = document.getElementById('categorySelect').value;
    
    showLoading();
    
    try {
        // Load map image
        const mapResponse = await fetch(`/api/debris-map?category=${category}`);
        const mapData = await mapResponse.json();
        
        if (mapData.success) {
            // Display map image
            document.getElementById('mapContainer').style.display = 'block';
            document.getElementById('debrisMapImage').src = mapData.image;
            
            // Update statistics
            document.getElementById('debrisStats').style.display = 'flex';
            document.getElementById('debrisCount').textContent = mapData.count.toLocaleString();
            document.getElementById('categoryName').textContent = categoryNames[category];
            
            // Determine density based on category
            // Category 1 & 2: High Density
            // Category 3 & 0: Mid Density
            // Category 4: Low Density
            let densityLevel;
            if (category === '1' || category === '2') {
                densityLevel = 'HIGH';
            } else if (category === '3' || category === '0') {
                densityLevel = 'MID';
            } else if (category === '4') {
                densityLevel = 'LOW';
            } else {
                densityLevel = 'VARIED'; // For "All Categories"
            }
            document.getElementById('coveragePercent').textContent = densityLevel;
            
            // Load interactive map data
            await loadInteractiveMap(category);
            
            showAlert(`Loaded ${mapData.count} debris objects`, 'success');
        } else {
            showAlert('Error: ' + mapData.error, 'danger');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

async function loadInteractiveMap(category) {
    try {
        const response = await fetch(`/api/debris-data?category=${category}`);
        const data = await response.json();
        
        if (data.success && data.debris.length > 0) {
            document.getElementById('interactiveMap').style.display = 'block';
            
            // Initialize or clear map
            if (leafletMapInstance) {
                leafletMapInstance.remove();
            }
            
            leafletMapInstance = L.map('leafletMap').setView([0, 0], 2);
            
            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18
            }).addTo(leafletMapInstance);
            
            // Add debris markers (limit to 500 for performance)
            const debrisToShow = data.debris.slice(0, 500);
            
            debrisToShow.forEach(debris => {
                const marker = L.circleMarker([debris.lat, debris.lon], {
                    radius: 3,
                    fillColor: getColorForAltitude(debris.alt),
                    color: '#000',
                    weight: 0.5,
                    opacity: 0.8,
                    fillOpacity: 0.6
                });
                
                marker.bindPopup(`
                    <strong>Debris Object</strong><br>
                    Altitude: ${debris.alt.toFixed(2)} km<br>
                    Category: ${debris.category}<br>
                    Lat: ${debris.lat.toFixed(2)}°<br>
                    Lon: ${debris.lon.toFixed(2)}°
                `);
                
                marker.addTo(leafletMapInstance);
            });
            
            if (debrisToShow.length < data.count) {
                showAlert(`Showing ${debrisToShow.length} of ${data.count} debris objects on interactive map`, 'info');
            }
        }
    } catch (error) {
        console.error('Error loading interactive map:', error);
    }
}

function getColorForAltitude(alt) {
    if (alt < 528) return '#FF0000';
    if (alt < 896) return '#FF8800';
    if (alt < 1264) return '#FFFF00';
    if (alt < 1632) return '#00FF00';
    return '#0000FF';
}

// Auto-load on page load
document.addEventListener('DOMContentLoaded', function() {
    // Optionally load default category
    // loadDebrisMap();
});
