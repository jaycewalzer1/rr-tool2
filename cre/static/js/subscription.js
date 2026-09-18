// Plan selection. The server creates the Checkout Session and returns its URL,
// so no Stripe.js bundle or publishable key is needed on this page.

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.subscribe-btn').forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            startCheckout(button);
        });
    });

    if (new URLSearchParams(window.location.search).get('cancelled')) {
        showFlashMessage('info', 'Checkout was cancelled.');
    }
});

async function startCheckout(button) {
    const originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = 'Processing...';

    try {
        const response = await fetch('/create-checkout-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
        });

        // An expired session renders the login page instead of JSON.
        if (!response.headers.get('content-type')?.includes('application/json')) {
            window.location.href = '/login';
            return;
        }

        const data = await response.json();
        if (!response.ok || !data.url) throw new Error(data.error || 'Could not start checkout');

        window.location.href = data.url;
    } catch (error) {
        button.textContent = originalLabel;
        button.disabled = false;
        showFlashMessage('error', error.message || 'Could not start checkout');
    }
}
