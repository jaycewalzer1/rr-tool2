from flask import Blueprint, render_template, url_for, session, jsonify, send_from_directory
import os
import stripe
from decorators import login_required, verify_account

misc_bp = Blueprint('misc', __name__)

@misc_bp.route("/contact")
def contact():
    return render_template("home/contact.html")

@misc_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@misc_bp.route('/')
def home():
    return render_template('home/index.html')

@misc_bp.route('/solutions')
def solutions():
    return render_template('home/solutions.html')

@misc_bp.route('/company')
def company():
    return render_template('home/company.html')

@misc_bp.route('/platform')
def platform():
    return render_template('home/platform.html')

@misc_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(misc_bp.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@misc_bp.route('/privacy')
def privacy():
    return render_template('home/privacy.html')

@misc_bp.route('/terms')
def terms():
    return render_template('home/terms.html')

@misc_bp.route('/create-checkout-session/<plan_id>', methods=['POST'])
def create_checkout_session(plan_id):
    try:
        # Define plan details - Replace these with your actual Stripe price IDs
        plans = {
            'basic': {
                'price_id': os.getenv('STRIPE_PRICE_ID_BASIC', 'price_1234567890abcdef'),  # Basic Plan - $9.99/month
                'amount': 999,  # $9.99
                'currency': 'usd',
                'interval': 'month'
            },
            'premium': {
                'price_id': os.getenv('STRIPE_PRICE_ID_PREMIUM', 'price_1234567890abcdef'),  # Premium Plan - $29.99/month
                'amount': 2999,  # $29.99
                'currency': 'usd',
                'interval': 'month'
            },
            'enterprise': {
                'price_id': os.getenv('STRIPE_PRICE_ID_ENTERPRISE', 'price_1234567890abcdef'),  # Enterprise Plan - $99.99/month
                'amount': 9999,  # $99.99
                'currency': 'usd',
                'interval': 'month'
            }
        }

        if plan_id not in plans:
            return jsonify(error='Invalid plan'), 400

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plans[plan_id]['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=session.get('email'),
            success_url=url_for('misc.success', _external=True),
            cancel_url=url_for('misc.cancel', _external=True),
            metadata={'user_id': session['user_id']}
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@misc_bp.route('/success')
def success():
    return render_template('home/success.html')

@misc_bp.route('/cancel')
def cancel():
    return render_template('home/cancel.html')

@misc_bp.route('/manage-subscription/<plan_id>')
@login_required
@verify_account
def manage_subscription(plan_id):
    try:
        customer = stripe.Customer.list(email=session['email']).data[0]
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv(f'STRIPE_PRICE_ID_{plan_id.upper()}'),
                'quantity': 1,
            }],
            mode='subscription',
            customer=customer.id,
            customer_email=session['email'],
            success_url=url_for('subscription', _external=True),
            cancel_url=url_for('subscription', _external=True),
            metadata={'user_id': session['user_id']}
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403
