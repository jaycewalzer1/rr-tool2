document.addEventListener('DOMContentLoaded', function() {
    console.log('Manage membership script loaded');
    loadSubscriptionStatus();
});

// Load subscription status
async function loadSubscriptionStatus() {
    try {
        const response = await fetch('/subscription/status');
        if (!response.ok) {
            throw new Error('Failed to load subscription status');
        }
        
        const data = await response.json();
        console.log('Subscription status:', data);
        
        const statusDiv = document.getElementById('subscription-status');
        const loadingDiv = statusDiv.querySelector('.status-loading');
        loadingDiv.remove();

        const statusContent = `
            <div class="status-content">
                <div class="status-item">
                    <strong>Current Plan:</strong> ${data.current_plan || 'No active subscription'}
                </div>
                <div class="status-item">
                    <strong>Status:</strong> ${data.status}
                </div>
                ${data.next_billing_date ? `
                <div class="status-item">
                    <strong>Next Billing:</strong> ${new Date(data.next_billing_date * 1000).toLocaleDateString()}
                </div>
                ` : ''}
                <div class="status-item">
                    <strong>Credits:</strong> ${data.upload_credits || 0}
                </div>
                ${data.last_payment_date ? `
                <div class="status-item">
                    <strong>Last Payment:</strong> ${new Date(data.last_payment_date * 1000).toLocaleDateString()}
                </div>
                ` : ''}
            </div>
        `;
        
        statusDiv.innerHTML = statusContent;
    } catch (error) {
        console.error('Error loading subscription status:', error);
        showError('Failed to load subscription status');
    }
}

// Change plan
async function changePlan() {
    try {
        const response = await fetch('/subscription/change-plan', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load plan options');
        }
        
        const data = await response.json();
        console.log('Plan options:', data);
        
        // Open Stripe checkout for plan change
        window.open(data.url, '_blank');
    } catch (error) {
        console.error('Error changing plan:', error);
        showError('Failed to change plan');
    }
}

// Cancel subscription
async function cancelSubscription() {
    if (!confirm('Are you sure you want to cancel your subscription? This will end your access at the end of your current billing cycle.')) {
        return;
    }

    try {
        const response = await fetch('/subscription/cancel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to cancel subscription');
        }
        
        const data = await response.json();
        console.log('Subscription cancelled:', data);
        
        // Refresh the page to show updated status
        window.location.reload();
    } catch (error) {
        console.error('Error cancelling subscription:', error);
        showError('Failed to cancel subscription');
    }
}

// View payment history
async function viewPaymentHistory() {
    try {
        const response = await fetch('/subscription/payment-history');
        if (!response.ok) {
            throw new Error('Failed to load payment history');
        }
        
        const data = await response.json();
        console.log('Payment history:', data);
        
        const historyDiv = document.getElementById('payment-history');
        const loadingDiv = historyDiv.querySelector('.history-loading');
        loadingDiv.remove();

        const payments = data.payments || [];
        const historyContent = `
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Invoice</th>
                    </tr>
                </thead>
                <tbody>
                    ${payments.map(payment => `
                    <tr>
                        <td>${new Date(payment.created * 1000).toLocaleDateString()}</td>
                        <td>$${(payment.amount / 100).toFixed(2)}</td>
                        <td>${payment.status}</td>
                        <td>
                            <a href="${payment.invoice_url}" target="_blank">View Invoice</a>
                        </td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        historyDiv.innerHTML = historyContent;
        historyDiv.style.display = 'block';
    } catch (error) {
        console.error('Error loading payment history:', error);
        showError('Failed to load payment history');
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.querySelector('.manage-membership').insertBefore(errorDiv, document.querySelector('.subscription-status'));

    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}
