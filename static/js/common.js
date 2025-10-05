/**
 * Common JavaScript Functions
 * Digunakan di semua halaman
 */

// Helper functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container.main-content');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Check if Font Awesome is loaded
window.addEventListener('DOMContentLoaded', function() {
    console.log('Checking Font Awesome...');
    setTimeout(function() {
        const faTest = document.querySelector('.fas, .fa');
        if (faTest) {
            const computed = window.getComputedStyle(faTest);
            console.log('Font Awesome font-family:', computed.fontFamily);
        }
    }, 1000);
});
