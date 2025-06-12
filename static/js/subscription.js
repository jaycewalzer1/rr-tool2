console.log('Subscription script loaded');

// Test function to verify script is loaded
window.subscriptionTest = function () {
    console.log('Subscription test function called');
    return 'Subscription script is loaded';
};

function initializeSubscription() {
    if (window.stripeInitialized) return;

    // Wait for Stripe to load
    if (typeof Stripe !== 'function') {
        console.log('Stripe not loaded yet, retrying...');
        setTimeout(initializeSubscription, 100);
        return;
    }

    // Get Stripe public key from meta tag
    const stripePublicKey = document.querySelector('meta[name="stripe-public-key"]');
    if (!stripePublicKey) {
        console.error('Stripe public key meta tag not found');
        return;
    }

    if (!stripePublicKey.content) {
        console.error('Stripe public key is empty');
        return;
    }

    console.log('Found Stripe public key:', stripePublicKey.content);
    const stripe = Stripe(stripePublicKey.content);
    console.log('Stripe initialized with key:', stripePublicKey.content);

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
            // Create Stripe Checkout session
            const checkoutResponse = await fetch(`/create-checkout-session/${planId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            const data = await checkoutResponse.json();

            if (!checkoutResponse.ok) {
                throw new Error(data.error || `HTTP ${checkoutResponse.status}: ${checkoutResponse.statusText}`);
            }

            if (!data.id) throw new Error('No checkout session ID returned');

            console.log('Redirecting to checkout with session ID:', data.id);
            stripe.redirectToCheckout({ sessionId: data.id });
        } catch (error) {
            console.error('Subscription error:', error);
            button.textContent = 'Subscribe';
            button.disabled = false;
            alert(error.message || 'An error occurred while processing your subscription');
        }
    }

    // Attach event listeners to all subscribe buttons
    const subscribeButtons = document.querySelectorAll('.subscribe-btn');
    if (subscribeButtons.length === 0) {
        console.error('No subscribe buttons found');
        return;
    }

    subscribeButtons.forEach(button => {
        const planId = button.closest('.plan-card')?.dataset?.planId;
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

    // Show cancellation alert if redirected with ?cancelled
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('cancelled')) {
        console.log('Cancellation message shown');
        alert('Subscription was cancelled.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded, initializing subscription');
    initializeSubscription();
});
