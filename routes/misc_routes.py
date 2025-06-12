from flask import Blueprint, render_template, url_for, session, jsonify, send_from_directory, redirect, flash, request
import os
import stripe
from decorators import login_required, verify_account
from auth import get_secret_hash, cognito, COGNITO_APP_CLIENT_ID
import boto3
import traceback

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/debug-session')
def debug_session():
    from flask import jsonify
    try:
        return jsonify({
            'session_keys': list(session.keys()),
            'pending_user_data': session.get('pending_user_data'),
            'user': session.get('user')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@misc_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        session_obj = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": os.getenv("STRIPE_PRICE_ID"),
                "quantity": 1,
            }],
            success_url="https://credatasolutionsx.com/success",
            cancel_url="https://credatasolutionsx.com/cancel",
        )
        return jsonify({'id': session_obj.id})
    
    except Exception as e:
        print("🚨 [EXCEPTION] Stripe checkout creation failed")
        print("❌ Error message:", str(e))
        print("🧵 Full traceback:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

    

@misc_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        print("[WEBHOOK ERROR] Invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print("[WEBHOOK ERROR] Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400

    print(f"[WEBHOOK] Received event: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        user_id = checkout_session.get('metadata', {}).get('user_id')
        print(f"[WEBHOOK] Subscription completed for user_id: {user_id}")

        # Optionally update DB here. Don't touch Flask session.

    return jsonify({'status': 'success'})

@misc_bp.route('/success')
def success():
    # Redirect to confirm signup instead of showing success page
    return redirect(url_for('auth.confirm_signup', subscription_completed=True))

@misc_bp.route('/cancel')
def cancel():
    flash('Subscription was cancelled.', 'info')
    return redirect(url_for('dashboard.subscription'))

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
            success_url=url_for('subscription', _external=True),
            cancel_url=url_for('subscription', _external=True),
            metadata={'user_id': session['user_id']}
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@misc_bp.route('/create-cognito-account', methods=['POST'])
def create_cognito_account():
    try:
        # Get user data from session
        user_data = session.get('pending_user_data')
        if not user_data:
            return jsonify({'error': 'No pending user data found'}), 400

        # Get Stripe subscription data from session
        stripe_data = session.get('stripe_subscription')
        if not stripe_data:
            return jsonify({'error': 'No Stripe subscription data found'}), 400

        # Create Cognito account
        username = user_data['username']
        password = user_data['password']
        secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)

        cognito.sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': user_data['email']},
                {'Name': 'phone_number', 'Value': user_data['phone_number']},
                {'Name': 'name', 'Value': user_data['name']},
                {'Name': 'preferred_username', 'Value': username}
            ],
            SecretHash=secret_hash
        )

        # Store user info in session
        session['user'] = {
            'email': user_data['email'],
            'username': username
        }
        
        # Clear pending data
        session.pop('pending_user_data', None)
        
        return jsonify({'status': 'success'})
        
    except cognito.exceptions.UsernameExistsException:
        return jsonify({'error': 'Username already exists'}), 400
    except cognito.exceptions.InvalidPasswordException:
        return jsonify({'error': 'Invalid password format'}), 400
    except Exception as e:
        print(f"Cognito account creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500
