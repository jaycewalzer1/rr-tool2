console.log('Subscription script loaded');

// Test function to verify script is loaded
window.subscriptionTest = function() {
    console.log('Subscription test function called');
    return 'Subscription script is loaded';
};

// Check if Stripe is loaded
function initializeSubscription() {
    if (window.stripeInitialized) return;
    
    // Wait for Stripe to load
    if (typeof Stripe !== 'function') {
        console.log('Stripe not loaded yet, retrying...');
        setTimeout(initializeSubscription, 100);
        return;
    }

    // Get Stripe key from meta tag
    const stripePublicKey = document.querySelector('meta[name="stripe-public-key"]');
    if (!stripePublicKey) {
        console.error('Stripe public key meta tag not found');
        return;
    }

    console.log('Found Stripe public key:', stripePublicKey.content);
    if (!stripePublicKey.content) {
        console.error('Stripe public key is empty');
        return;
    }

    // Initialize Stripe
    const stripe = Stripe(stripePublicKey.content);
    console.log('Stripe initialized with key:', stripePublicKey.content);

    // Set flag to prevent reinitialization
    window.stripeInitialized = true;

    async function subscribe(planId) {
        console.log('Subscribe called for plan:', planId);
        const button = document.querySelector(`.plan-card[data-plan-id="${planId}"] .subscribe-btn`);
        if (!button) {
            console.error('Subscribe button not found for plan:', planId);
            return;
        }

        button.disabled = true;
        button.textContent = 'Processing...';

        try {
            // Get user data from session
            const response = await fetch('/api/user/check-session', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Please log in to subscribe');
            }

            const userData = await response.json();
            if (!userData.user) {
                throw new Error('User data not found in session');
            }

            // Create checkout session
            const checkoutResponse = await fetch(`/create-checkout-session/${planId}`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!checkoutResponse.ok) {
                const errorData = await checkoutResponse.json();
                throw new Error(errorData.error || `HTTP ${checkoutResponse.status}: ${checkoutResponse.statusText}`);
            }

            const data = await checkoutResponse.json();
            if (!data.id) throw new Error('No checkout session ID returned');

            console.log('Redirecting to checkout');
            stripe.redirectToCheckout({ sessionId: data.id });
        } catch (error) {
            console.error('Subscription error:', error);
            button.textContent = 'Subscribe';
            button.disabled = false;
            alert(error.message || 'An error occurred while processing your subscription');
        }
    }

    // Add event listeners to all subscribe buttons
    const subscribeButtons = document.querySelectorAll('.subscribe-btn');
    if (subscribeButtons.length === 0) {
        console.error('No subscribe buttons found');
        return;
    }

    subscribeButtons.forEach(button => {
        const planId = button.closest('.plan-card').dataset.planId;
        if (!planId) {
            console.error('Plan ID not found on button:', button);
            return;
        }

        button.addEventListener('click', async (e) => {
            e.preventDefault();
            console.log('Button clicked for plan:', planId);
            await subscribe(planId);
        });
    });

    // Handle cancellation message
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('cancelled')) {
        console.log('Cancellation message shown');
        alert('Subscription was cancelled.');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded, initializing subscription');
    initializeSubscription();
});
