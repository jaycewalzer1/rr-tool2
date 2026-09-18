// Home page specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize home page functionality
    initializeHomePage();
});

// Initialize home page
function initializeHomePage() {
    // Add any home page specific event listeners here
    setupSmoothScroll();
    setupPartnerLogos();
}

// Smooth scroll for navigation links
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Setup partner logos animation
function setupPartnerLogos() {
    const partnerLogos = document.querySelector('.partner-logos');
    if (partnerLogos) {
        partnerLogos.addEventListener('mouseenter', function() {
            this.classList.add('animate-logos');
        });
        
        partnerLogos.addEventListener('mouseleave', function() {
            this.classList.remove('animate-logos');
        });
    }
}

// Handle form submissions
async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });
        
        await handleApiError(response);
        
        // Handle successful submission
        showFlashMessage('success', 'Thank you for your submission!');
        form.reset();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to submit form');
    }
}
