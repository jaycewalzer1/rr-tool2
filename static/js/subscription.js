console.log('Subscription script loaded');

function initializeSubscription() {
    if (window.stripeInitialized) return;

    if (typeof Stripe !== 'function') {
        console.log('Stripe not loaded yet, retrying...');
        setTimeout(initializeSubscription, 100);
        return;
    }

    const stripePublicKey = document.querySelector('meta[name="stripe-public-key"]');
    if (!stripePublicKey || !stripePublicKey.content) {
        console.error('Stripe public key not found or empty');
        return;
    }

    const stripe = Stripe(stripePublicKey.content);
    window.stripeInitialized = true;
    console.log('Stripe initialized with key:', stripePublicKey.content);

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
            const rawText = await checkoutResponse.text();
            console.warn("⚠️ RAW RESPONSE:", rawText.slice(0, 300));

            if (!checkoutResponse.ok) {
                throw new Error(`Bad response: ${checkoutResponse.status}`);
            }

            if (!contentType.includes('application/json')) {
                throw new Error("Unexpected response format: expected JSON, received HTML");
            }

            const data = JSON.parse(rawText);
            if (!data.id) throw new Error('No checkout session ID returned');

            console.log('Redirecting to Stripe checkout...');
            stripe.redirectToCheckout({ sessionId: data.id });
        } catch (error) {
            console.error('Subscription error:', error);
            button.textContent = 'Subscribe';
            button.disabled = false;
            alert(error.message || 'An error occurred while processing your subscription');
        }
    }

    const subscribeButtons = document.querySelectorAll('.subscribe-btn');
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

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('cancelled')) {
        alert('Subscription was cancelled.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded, initializing subscription');
    initializeSubscription();
});
