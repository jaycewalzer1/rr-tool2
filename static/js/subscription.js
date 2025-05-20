const stripe = Stripe("{{ publishable_key }}");

const urlParams = new URLSearchParams(window.location.search);
const cancelled = urlParams.get('cancelled');

if (cancelled) {
    flashMessage('Subscription cancelled.', 'info');
}

document.addEventListener('DOMContentLoaded', () => {
    loadSubscriptionStatus();
    loadPaymentHistory();
});

function flashMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message ${type}`;
    messageDiv.textContent = message;

    const statusDiv = document.getElementById('subscription-status');
    if (statusDiv) {
        statusDiv.insertBefore(messageDiv, statusDiv.firstChild);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

async function loadSubscriptionStatus() {
    try {
        const response = await fetch('/subscription/status');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load subscription status');
        }

        const statusDiv = document.getElementById('subscription-status');
        if (!statusDiv) {
            throw new Error('Subscription status container not found');
        }

        if (data.error) {
            statusDiv.innerHTML = `
                <div class="status-item">
                    <span class="label">Status:</span>
                    <span class="value error">${data.error}</span>
                </div>
                <div class="status-item">
                    <span class="label">Message:</span>
                    <span class="value">${data.message || 'Unknown error'}</span>
                </div>
            `;
            return;
        }

        const plan = data.plan || {};
        statusDiv.innerHTML = `
            <div class="status-item">
                <span class="label">Status:</span>
                <span class="value ${data.status === 'inactive' ? 'inactive' : ''}">${data.status}</span>
            </div>
            <div class="status-item">
                <span class="label">Current Plan:</span>
                <span class="value">${plan.nickname || 'None'}</span>
            </div>
            <div class="status-item">
                <span class="label">Amount:</span>
                <span class="value">${(plan.amount / 100).toFixed(2)} ${plan.currency?.toUpperCase() || 'USD'}</span>
            </div>
            <div class="status-item">
                <span class="label">Next Billing Date:</span>
                <span class="value">${data.current_period_end ? new Date(data.current_period_end * 1000).toLocaleDateString() : 'N/A'}</span>
            </div>
        `;

        document.querySelectorAll('.subscribe-btn').forEach(button => {
            const planId = button.closest('.plan-card').dataset.planId;
            if (plan.id === planId) {
                button.textContent = 'Manage Subscription';
                button.onclick = () => manageSubscription(planId);
            } else {
                button.textContent = 'Subscribe';
                button.onclick = () => subscribe(planId);
            }
        });
    } catch (error) {
        console.error('Error loading subscription status:', error);
        const statusDiv = document.getElementById('subscription-status');
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="status-item">
                    <span class="label">Status:</span>
                    <span class="value error">Error</span>
                </div>
                <div class="status-item">
                    <span class="label">Message:</span>
                    <span class="value">${error.message || 'Failed to load subscription status'}</span>
                </div>
            `;
        }
    }
}

async function manageSubscription(planId) {
    try {
        const { sessionId } = await fetch(`/manage-subscription/${planId}`).then(r => r.json());
        await stripe.redirectToCheckout({ sessionId });
    } catch (error) {
        alert('Error managing subscription: ' + error.message);
    }
}

async function subscribe(planId) {
    try {
        const button = document.querySelector(`.plan-card[data-plan-id="${planId}"] .subscribe-btn`);
        if (button) {
            button.disabled = true;
            button.textContent = 'Processing...';
        }

        const response = await fetch(`/create-checkout-session/${planId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (!response.ok || data.error || !data.url) {
            throw new Error(data.error || 'Checkout session creation failed.');
        }

        // Open Stripe Checkout in a new tab
        window.open(data.url, '_blank');

    } catch (error) {
        console.error('Subscription error:', error);

        const button = document.querySelector(`.plan-card[data-plan-id="${planId}"] .subscribe-btn`);
        if (button) {
            button.disabled = false;
            button.textContent = 'Subscribe';

            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = error.message || 'An error occurred.';
            button.parentElement.insertBefore(errorDiv, button.nextSibling);
        }
    }
}