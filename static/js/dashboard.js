/**
 * Dashboard/Index Page JavaScript
 */

// Load statistics
document.addEventListener('DOMContentLoaded', function() {
    // Simulate loading statistics
    setTimeout(() => {
        const totalSatellites = document.getElementById('totalSatellites');
        const totalDebris = document.getElementById('totalDebris');
        const safePredictions = document.getElementById('safePredictions');
        const collisionAlerts = document.getElementById('collisionAlerts');
        
        if (totalSatellites) totalSatellites.textContent = '1';
        if (totalDebris) totalDebris.textContent = '3,500+';
        if (safePredictions) safePredictions.textContent = '0';
        if (collisionAlerts) collisionAlerts.textContent = '0';
    }, 500);
});
