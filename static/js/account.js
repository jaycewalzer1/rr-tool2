// Account page specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize account page functionality
    initializeAccountPage();
});

// Initialize account page
function initializeAccountPage() {
    // Add any account page specific event listeners here
    setupResendCode();
}

// Setup resend code functionality
function setupResendCode() {
    const resendButtons = document.querySelectorAll('.resend-button');
    resendButtons.forEach(button => {
        button.addEventListener('click', handleResendCode);
    });
}

// Handle resend code
async function handleResendCode(e) {
    e.preventDefault();
    const button = e.currentTarget;
    const username = button.getAttribute('data-username');

    try {
        const response = await fetch('/auth/resend-confirmation-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username
            })
        });

        const data = await handleApiError(response);
        
        showFlashMessage('success', 'Confirmation code has been resent to your email!');
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to resend code');
    }
}

// Handle form submissions
async function handleAccountFormSubmit(event) {
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
        showFlashMessage('success', 'Form submitted successfully');
        // Redirect or update UI as needed
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to submit form');
    }
}

// Validate confirmation code
function validateConfirmationCode(code) {
    // Basic validation
    if (!code || code.length !== 6) {
        return false;
    }
    return true;
}
