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
    if (!stripePublicKey || !stripePublicKey.content) {
        console.error('Stripe public key not found or empty');
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
            const checkoutResponse = await fetch(`/create-checkout-session/${planId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            const contentType = checkoutResponse.headers.get('content-type') || '';

            if (!checkoutResponse.ok) {
                let message = `HTTP ${checkoutResponse.status}: ${checkoutResponse.statusText}`;

                if (contentType.includes('application/json')) {
                    const errorData = await checkoutResponse.json();
                    message = errorData.error || message;
                } else {
                    const rawText = await checkoutResponse.text();
                    console.warn('⚠️ Received non-JSON error response:', rawText.slice(0, 200));
                }

                throw new Error(message);
            }

            if (!contentType.includes('application/json')) {
                const rawText = await checkoutResponse.text();
                throw new Error('Unexpected response format: expected JSON, received HTML');
            }

            const data = await checkoutResponse.json();

            if (!data.id) {
                throw new Error('No checkout session ID returned from server');
            }

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
            console.error('Plan ID not found for button:', button);
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
