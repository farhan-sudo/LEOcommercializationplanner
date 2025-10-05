/**
 * Passing Time Page JavaScript
 */

// Store pass data for export
let currentPassData = [];
let currentSatelliteName = '';

// Load example data
function loadExampleData() {
    document.getElementById('satName').value = 'ISS (ZARYA)';
    document.getElementById('tleLine1').value = '1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997';
    document.getElementById('tleLine2').value = '2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172';
    document.getElementById('latitude').value = '-6.200000';
    document.getElementById('longitude').value = '106.816666';
    document.getElementById('elevation').value = '5';
    document.getElementById('minElevation').value = '10';
    
    // Set default start time to now (UTC)
    setCurrentTime();
    document.getElementById('searchDuration').value = '24';
    
    showAlert('Example data loaded (ISS over Jakarta)', 'info');
}

// Set current time
function setCurrentTime() {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toISOString().split('T')[1].substring(0, 5);
    document.getElementById('startDate').value = dateStr;
    document.getElementById('startTime').value = timeStr;
}

// Set location preset
function setLocation(lat, lon, elev, name) {
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lon;
    document.getElementById('elevation').value = elev;
    showAlert(`Location set to ${name}`, 'success');
}

// Form submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('passingTimeForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            calculatePasses();
        });
    }
    
    // Auto-load example on page load
    loadExampleData();
});

// Calculate passes
async function calculatePasses() {
    const satName = document.getElementById('satName').value.trim();
    const tleLine1 = document.getElementById('tleLine1').value.trim();
    const tleLine2 = document.getElementById('tleLine2').value.trim();
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);
    const elevation = parseFloat(document.getElementById('elevation').value);
    const minElevation = parseFloat(document.getElementById('minElevation').value);
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const searchDuration = parseFloat(document.getElementById('searchDuration').value);
    
    if (!tleLine1 || !tleLine2) {
        showAlert('Please enter both TLE lines', 'warning');
        return;
    }
    
    if (isNaN(latitude) || isNaN(longitude) || isNaN(elevation)) {
        showAlert('Please enter valid coordinates', 'warning');
        return;
    }
    
    if (!startDate || !startTime) {
        showAlert('Please enter start date and time', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/calculate-passes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tle_name: satName,
                tle_line1: tleLine1,
                tle_line2: tleLine2,
                latitude: latitude,
                longitude: longitude,
                elevation: elevation,
                min_elevation: minElevation,
                start_date: startDate,
                start_time: startTime,
                search_duration: searchDuration
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPasses(data.passes, minElevation, latitude, longitude);
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Display passes results
function displayPasses(passes, minElev, lat, lon) {
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('displayMinElev').textContent = minElev;
    document.getElementById('displayLocation').textContent = `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`;
    
    // Display search period
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const duration = document.getElementById('searchDuration').value;
    const startDateTime = new Date(`${startDate}T${startTime}:00Z`);
    const endDateTime = new Date(startDateTime.getTime() + duration * 60 * 60 * 1000);
    
    document.getElementById('displaySearchPeriod').innerHTML = 
        `From: <strong>${startDateTime.toISOString().replace('T', ' ').substring(0, 19)} UTC</strong><br>` +
        `To: <strong>${endDateTime.toISOString().replace('T', ' ').substring(0, 19)} UTC</strong> (${duration} hours)`;
    
    // Store data for export
    currentPassData = passes;
    currentSatelliteName = document.getElementById('satName').value;
    
    // Show export button
    document.getElementById('exportBtn').style.display = 'inline-block';
    
    const container = document.getElementById('passesContainer');
    
    if (passes.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-info-circle"></i> 
                <strong>No passes found</strong> above ${minElev}° elevation in the selected ${duration}-hour period.
                <hr>
                <p class="mb-0"><strong>Suggestions:</strong></p>
                <ul class="mb-0">
                    <li>Try lowering the minimum elevation angle</li>
                    <li>Extend the search duration to 48 or 72 hours</li>
                    <li>Choose a different start time</li>
                    <li>Verify the TLE data is current</li>
                </ul>
            </div>
        `;
        return;
    }
    
    // Calculate statistics
    const totalDuration = passes.reduce((sum, pass) => sum + parseFloat(pass.duration_minutes), 0);
    const avgDuration = (totalDuration / passes.length).toFixed(2);
    const maxElevation = Math.max(...passes.map(p => parseFloat(p.max_alt_degrees)));
    
    let html = `
        <!-- Summary Statistics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card border-primary">
                    <div class="card-body text-center">
                        <i class="fas fa-satellite fa-2x text-primary mb-2"></i>
                        <h3 class="mb-0">${passes.length}</h3>
                        <small class="text-muted">Total Passes</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-success">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x text-success mb-2"></i>
                        <h3 class="mb-0">${totalDuration.toFixed(1)}</h3>
                        <small class="text-muted">Total Minutes</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-info">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-line fa-2x text-info mb-2"></i>
                        <h3 class="mb-0">${avgDuration}</h3>
                        <small class="text-muted">Avg Duration (min)</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-warning">
                    <div class="card-body text-center">
                        <i class="fas fa-angle-up fa-2x text-warning mb-2"></i>
                        <h3 class="mb-0">${maxElevation.toFixed(1)}°</h3>
                        <small class="text-muted">Best Elevation</small>
                    </div>
                </div>
            </div>
        </div>
        
        <h5 class="mb-3"><i class="fas fa-list"></i> Detailed Pass Information</h5>
    `;
    
    passes.forEach((pass, index) => {
        const qualityClass = getPassQuality(parseFloat(pass.max_alt_degrees));
        
        html += generatePassCard(pass, index, qualityClass, minElev);
    });
    
    container.innerHTML = html;
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Generate pass card HTML
function generatePassCard(pass, index, qualityClass, minElev) {
    return `
        <div class="card mb-3 border-${qualityClass}">
            <div class="card-header bg-${qualityClass} text-white">
                <h5 class="mb-0">
                    <i class="fas fa-satellite"></i> Pass #${index + 1} 
                    <span class="badge bg-dark float-end">Max Elevation: ${pass.max_alt_degrees}°</span>
                </h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <!-- AOS Time -->
                    <div class="col-md-4">
                        <div class="border rounded p-3 bg-light h-100">
                            <h6 class="text-success mb-2">
                                <i class="fas fa-arrow-up"></i> AOS (Acquisition of Signal)
                            </h6>
                            <div class="fs-5 fw-bold text-dark">${formatTime(pass.aos_time)}</div>
                            <small class="text-muted">Satellite rises above ${minElev}°</small>
                        </div>
                    </div>
                    
                    <!-- Max Altitude Time -->
                    <div class="col-md-4">
                        <div class="border rounded p-3 bg-light h-100">
                            <h6 class="text-warning mb-2">
                                <i class="fas fa-angle-up"></i> Maximum Elevation
                            </h6>
                            <div class="fs-5 fw-bold text-dark">${formatTime(pass.max_alt_time, true)}</div>
                            <div class="text-primary fw-bold">${pass.max_alt_degrees}° @ ${pass.max_azimuth_degrees}° azimuth</div>
                            <small class="text-muted">Best viewing time</small>
                        </div>
                    </div>
                    
                    <!-- LOS Time -->
                    <div class="col-md-4">
                        <div class="border rounded p-3 bg-light h-100">
                            <h6 class="text-danger mb-2">
                                <i class="fas fa-arrow-down"></i> LOS (Loss of Signal)
                            </h6>
                            <div class="fs-5 fw-bold text-dark">${formatTime(pass.los_time)}</div>
                            <small class="text-muted">Satellite drops below ${minElev}°</small>
                        </div>
                    </div>
                </div>
                
                <!-- Additional Info -->
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-clock text-primary fs-4 me-2"></i>
                            <div>
                                <strong>Duration:</strong> ${pass.duration_minutes} minutes<br>
                                <small class="text-muted">Total visibility time</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-compass text-info fs-4 me-2"></i>
                            <div>
                                <strong>Direction:</strong> ${getDirectionFromAzimuth(parseFloat(pass.max_azimuth_degrees))}<br>
                                <small class="text-muted">${pass.max_azimuth_degrees}° azimuth</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-3">
                    ${getPassDescription(parseFloat(pass.max_alt_degrees))}
                </div>
                
                <!-- Timeline Table -->
                <div class="mt-3">
                    <h6 class="mb-2"><i class="fas fa-list"></i> Pass Timeline</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th width="30%">Event</th>
                                    <th width="35%">Time (UTC)</th>
                                    <th width="35%">Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="table-success">
                                    <td><i class="fas fa-arrow-up text-success"></i> <strong>AOS Start</strong></td>
                                    <td class="fw-bold">${pass.aos_time}</td>
                                    <td>Satellite rises above ${minElev}° elevation</td>
                                </tr>
                                <tr class="table-warning">
                                    <td><i class="fas fa-angle-up text-warning"></i> <strong>Maximum</strong></td>
                                    <td class="fw-bold">${pass.aos_time.split(' ')[0]} ${pass.max_alt_time}</td>
                                    <td>Peak at ${pass.max_alt_degrees}° elevation, ${pass.max_azimuth_degrees}° azimuth (${getDirectionFromAzimuth(parseFloat(pass.max_azimuth_degrees))})</td>
                                </tr>
                                <tr class="table-danger">
                                    <td><i class="fas fa-arrow-down text-danger"></i> <strong>LOS End</strong></td>
                                    <td class="fw-bold">${pass.los_time}</td>
                                    <td>Satellite drops below ${minElev}° elevation</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Helper functions
function formatTime(timeString, shortFormat = false) {
    const parts = timeString.split(' ');
    
    if (shortFormat && parts.length === 3) {
        return parts[0];
    }
    
    if (parts.length === 3) {
        const date = parts[0];
        const time = parts[1];
        return `${date} ${time}`;
    } else if (parts.length === 2) {
        return parts[0];
    }
    
    return timeString;
}

function getDirectionFromAzimuth(azimuth) {
    const directions = [
        'North', 'NNE', 'NE', 'ENE',
        'East', 'ESE', 'SE', 'SSE',
        'South', 'SSW', 'SW', 'WSW',
        'West', 'WNW', 'NW', 'NNW'
    ];
    const index = Math.round(azimuth / 22.5) % 16;
    return directions[index];
}

function getPassQuality(maxAlt) {
    if (maxAlt >= 60) return 'success';
    if (maxAlt >= 45) return 'primary';
    if (maxAlt >= 30) return 'info';
    if (maxAlt >= 20) return 'warning';
    return 'secondary';
}

function getPassDescription(maxAlt) {
    if (maxAlt >= 60) {
        return '<span class="badge bg-success"><i class="fas fa-star"></i> Excellent Pass</span> - Directly overhead, perfect for observation';
    } else if (maxAlt >= 45) {
        return '<span class="badge bg-primary"><i class="fas fa-check"></i> Very Good Pass</span> - High in the sky, great visibility';
    } else if (maxAlt >= 30) {
        return '<span class="badge bg-info"><i class="fas fa-thumbs-up"></i> Good Pass</span> - Moderate altitude, good viewing conditions';
    } else if (maxAlt >= 20) {
        return '<span class="badge bg-warning"><i class="fas fa-adjust"></i> Fair Pass</span> - Lower altitude, may be affected by obstructions';
    } else {
        return '<span class="badge bg-secondary"><i class="fas fa-eye-slash"></i> Low Pass</span> - Near horizon, difficult to observe';
    }
}

// Export pass data to CSV
function exportPassData() {
    if (currentPassData.length === 0) {
        showAlert('No pass data to export', 'warning');
        return;
    }
    
    // Create CSV content
    let csv = 'Satellite Passing Times Report\n';
    csv += `Satellite: ${currentSatelliteName}\n`;
    csv += `Location: ${document.getElementById('displayLocation').textContent}\n`;
    csv += `Minimum Elevation: ${document.getElementById('displayMinElev').textContent}°\n`;
    csv += `Generated: ${new Date().toUTCString()}\n\n`;
    csv += 'Pass #,AOS Time (UTC),Max Elevation Time (UTC),LOS Time (UTC),Max Elevation (°),Azimuth (°),Direction,Duration (min)\n';
    
    currentPassData.forEach((pass, index) => {
        csv += `${index + 1},`;
        csv += `"${pass.aos_time}",`;
        csv += `"${pass.aos_time.split(' ')[0]} ${pass.max_alt_time}",`;
        csv += `"${pass.los_time}",`;
        csv += `${pass.max_alt_degrees},`;
        csv += `${pass.max_azimuth_degrees},`;
        csv += `${getDirectionFromAzimuth(parseFloat(pass.max_azimuth_degrees))},`;
        csv += `${pass.duration_minutes}\n`;
    });
    
    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `satellite_passes_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showAlert('Pass data exported successfully!', 'success');
}
