/**
 * Satellite Tracking Page JavaScript
 */

let trackingMapInstance = null;
let satelliteMarker = null;
let autoUpdateInterval = null;
let currentTLE = { line1: '', line2: '' };

function loadExampleTLE() {
    document.getElementById('tleLine1').value = '1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997';
    document.getElementById('tleLine2').value = '2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172';
    showAlert('Example TLE data loaded (ISS)', 'info');
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('trackingForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            startTracking();
        });
    }
});

async function startTracking() {
    const tleLine1 = document.getElementById('tleLine1').value.trim();
    const tleLine2 = document.getElementById('tleLine2').value.trim();
    
    if (!tleLine1 || !tleLine2) {
        showAlert('Please enter both TLE lines', 'warning');
        return;
    }
    
    currentTLE.line1 = tleLine1;
    currentTLE.line2 = tleLine2;
    
    await updateSatellitePosition();
    
    // Enable auto-update button
    const autoBtn = document.getElementById('autoUpdateBtn');
    if (autoBtn) {
        autoBtn.disabled = false;
    }
    
    showAlert('Tracking started successfully', 'success');
}

async function updateSatellitePosition() {
    try {
        const response = await fetch('/api/satellite-position', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tle_line1: currentTLE.line1,
                tle_line2: currentTLE.line2
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPosition(data);
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    }
}

function displayPosition(data) {
    // Show position section
    const posSection = document.getElementById('positionSection');
    if (posSection) {
        posSection.style.display = 'flex';
    }
    
    const pos = data.position;
    
    // Update text information
    const elements = {
        'currentTime': data.time,
        'currentLat': pos.lat.toFixed(4) + '°',
        'currentLon': pos.lon.toFixed(4) + '°',
        'currentAlt': pos.alt.toFixed(2) + ' km',
        'orbitalPeriod': data.orbital_period.toFixed(2) + ' minutes',
        'posX': pos.x.toFixed(2),
        'posY': pos.y.toFixed(2),
        'posZ': pos.z.toFixed(2),
        'lastUpdate': new Date().toLocaleTimeString()
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }
    
    const statusElement = document.getElementById('updateStatus');
    if (statusElement) {
        statusElement.innerHTML = '<i class="fas fa-check-circle text-success"></i> Updated successfully';
    }
    
    // Initialize or update map
    const mapContainer = document.getElementById('trackingMap');
    if (!mapContainer) return;
    
    if (!trackingMapInstance) {
        trackingMapInstance = L.map('trackingMap').setView([pos.lat, pos.lon], 4);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(trackingMapInstance);
        
        // Create satellite marker
        const satelliteIcon = L.divIcon({
            className: 'satellite-marker',
            html: '<i class="fas fa-satellite fa-2x text-primary"></i>',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });
        
        satelliteMarker = L.marker([pos.lat, pos.lon], {
            icon: satelliteIcon
        }).addTo(trackingMapInstance);
        
        satelliteMarker.bindPopup(`
            <strong>Satellite Position</strong><br>
            Lat: ${pos.lat.toFixed(4)}°<br>
            Lon: ${pos.lon.toFixed(4)}°<br>
            Alt: ${pos.alt.toFixed(2)} km
        `).openPopup();
    } else {
        // Update existing marker
        satelliteMarker.setLatLng([pos.lat, pos.lon]);
        trackingMapInstance.setView([pos.lat, pos.lon]);
        
        satelliteMarker.getPopup().setContent(`
            <strong>Satellite Position</strong><br>
            Lat: ${pos.lat.toFixed(4)}°<br>
            Lon: ${pos.lon.toFixed(4)}°<br>
            Alt: ${pos.alt.toFixed(2)} km
        `);
    }
}

function toggleAutoUpdate() {
    const btn = document.getElementById('autoUpdateBtn');
    
    if (autoUpdateInterval) {
        // Stop auto-update
        clearInterval(autoUpdateInterval);
        autoUpdateInterval = null;
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Auto Update: OFF';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-success');
        showAlert('Auto-update stopped', 'info');
    } else {
        // Start auto-update (every 5 seconds)
        autoUpdateInterval = setInterval(updateSatellitePosition, 5000);
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Auto Update: ON';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-danger');
        showAlert('Auto-update started (every 5 seconds)', 'success');
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (autoUpdateInterval) {
        clearInterval(autoUpdateInterval);
    }
});
