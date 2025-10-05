/**
 * Collision Prediction Page JavaScript
 */

// Example TLE data (ISS)
function loadExampleTLE() {
    document.getElementById('tleLine1').value = '1 25544U 98067A   25277.85315669  .00012686  00000+0  23245-3 0  9997';
    document.getElementById('tleLine2').value = '2 25544  51.6326 123.5365 0000933 203.2133 156.8813 15.49682341532172';
    showAlert('Example TLE data loaded (ISS - International Space Station)', 'info');
}

// Form submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('collisionForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            predictCollision();
        });
    }
});

async function predictCollision() {
    const tleLine1 = document.getElementById('tleLine1').value.trim();
    const tleLine2 = document.getElementById('tleLine2').value.trim();
    const numPeriods = parseInt(document.getElementById('numPeriods').value);
    const timeStep = parseInt(document.getElementById('timeStep').value);
    const threshold = parseFloat(document.getElementById('threshold').value);
    
    if (!tleLine1 || !tleLine2) {
        showAlert('Please enter both TLE lines', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/predict-collision', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tle_line1: tleLine1,
                tle_line2: tleLine2,
                num_periods: numPeriods,
                time_step: timeStep,
                threshold: threshold
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data, threshold);
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

function displayResults(data, threshold) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update status alert
    const statusAlert = document.getElementById('statusAlert');
    if (data.collision) {
        statusAlert.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-circle"></i> DANGER - COLLISION DETECTED!</h5>
                <p class="mb-0">Potential collision with space debris detected. Immediate action required.</p>
            </div>
        `;
    } else {
        statusAlert.innerHTML = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> SUCCESS - SAFE FROM COLLISION!</h5>
                <p class="mb-0">No collision detected. Satellite path is safe.</p>
            </div>
        `;
    }
    
    // Update statistics
    document.getElementById('statMinDistance').textContent = data.min_distance.toFixed(2);
    document.getElementById('statCollisionCount').textContent = data.collision_count;
    
    const safetyMargin = data.min_distance - threshold;
    document.getElementById('statSafetyMargin').textContent = safetyMargin.toFixed(2);
    
    document.getElementById('statStatus').innerHTML = data.collision ? 
        '<i class="fas fa-times-circle text-danger"></i>' : 
        '<i class="fas fa-check-circle text-success"></i>';
    
    // Display closest point details
    if (data.closest_point) {
        const cp = data.closest_point;
        const detailsHTML = `
            <div class="card bg-light">
                <div class="card-body">
                    <h5><i class="fas fa-crosshairs"></i> Closest Approach Details</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Time:</strong> ${cp.time}</p>
                            <p><strong>Latitude:</strong> ${cp.lat.toFixed(2)}°</p>
                            <p><strong>Longitude:</strong> ${cp.lon.toFixed(2)}°</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Altitude:</strong> ${cp.alt.toFixed(2)} km</p>
                            <p><strong>Position:</strong> (${cp.x.toFixed(2)}, ${cp.y.toFixed(2)}, ${cp.z.toFixed(2)}) km</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('detailsContainer').innerHTML = detailsHTML;
    }
    
    // Display collision points table
    if (data.collision_points && data.collision_points.length > 0) {
        document.getElementById('collisionPointsContainer').style.display = 'block';
        
        let tableHTML = '';
        data.collision_points.forEach((point, index) => {
            tableHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${point.time}</td>
                    <td><span class="badge bg-danger">${point.distance.toFixed(2)}</span></td>
                    <td>${point.sat_pos.lat.toFixed(2)}°</td>
                    <td>${point.sat_pos.lon.toFixed(2)}°</td>
                    <td>${point.sat_pos.alt.toFixed(2)}</td>
                </tr>
            `;
        });
        document.getElementById('collisionPointsTable').innerHTML = tableHTML;
    } else {
        document.getElementById('collisionPointsContainer').style.display = 'none';
    }
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}
