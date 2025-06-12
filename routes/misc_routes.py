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


@misc_bp.route('/create-checkout-session/<plan_id>', methods=['POST'])
def create_checkout_session(plan_id):
    try:
        # Debug: log session contents
        print(f"== SESSION KEYS: {list(session.keys())} ==")
        print(f"== USER: {session.get('user')}")
        print(f"== PENDING USER: {session.get('pending_user_data')}")

        # Get user data from either full auth or pending signup
        user = session.get('user') or session.get('pending_user_data')

        if not user:
            print("[AUTH] No user found in session")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'User session missing'}), 401
            return redirect(url_for('misc.home'))

        # Plan lookup
        plans = {
            'basic': {
                'price_id': os.getenv('STRIPE_PRICE_ID_BASIC'),
                'amount': 1,
                'currency': 'usd',
                'interval': 'month'
            }
        }

        print(f"[DEBUG] Requested plan_id: {plan_id}")
        if plan_id not in plans:
            print("[ERROR] Invalid plan ID requested")
            return jsonify({'error': 'Invalid plan'}), 400

        selected_plan = plans[plan_id]
        print(f"[DEBUG] Selected plan: {selected_plan}")

        user_id = user.get('sub') or user.get('cognito_user_id') or user.get('username')
        user_email = user.get('email')
        user_name = user.get('name')

        print(f"[DEBUG] user_id: {user_id}, email: {user_email}")

        # Get or create Stripe customer
        customer_list = stripe.Customer.list(email=user_email).data
        if not customer_list:
            customer = stripe.Customer.create(
                email=user_email,
                name=user_name or 'Unknown User',
                metadata={'user_id': user_id}
            )
            print(f"[STRIPE] Created new customer: {customer.id}")
        else:
            customer = customer_list[0]
            print(f"[STRIPE] Found existing customer: {customer.id}")

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': selected_plan['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            customer=customer.id,
            success_url=f"{request.host_url}confirm-signup?subscription_completed=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=request.host_url.rstrip('/') + '/subscription',
            metadata={'user_id': user_id}
        )

        session['stripe_session_id'] = checkout_session.id
        print(f"[SUCCESS] Created Stripe Checkout Session ID: {checkout_session.id}")
        return jsonify({'id': checkout_session.id})

    except Exception as e:
        print(f"[EXCEPTION] Stripe checkout creation failed: {str(e)}")
        print("[TRACEBACK]")
        print(traceback.format_exc())  # Print full stack trace
        return jsonify({'error': 'An unexpected error occurred'}), 500
    



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
