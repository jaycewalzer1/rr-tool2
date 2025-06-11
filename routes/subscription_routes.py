from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template
import stripe
import os
from datetime import datetime
from decorators import login_required, verify_account
import traceback

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.data
        event = None

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), STRIPE_SECRET_KEY
            )
        except ValueError as e:
            print(f"Error parsing webhook payload: {str(e)}")
            return jsonify(error='Invalid payload'), 400

        print(f"Received webhook event: {event.type}")

        # Handle different event types
        if event.type == 'checkout.session.completed':
            checkout_session = event.data.object
            customer = stripe.Customer.retrieve(checkout_session.customer)
            
            # In test mode, we need to wait for the subscription to be created
            # So we'll just update the customer metadata with basic info
            stripe.Customer.modify(
                customer.id,
                metadata={
                    'subscription_status': 'pending',
                    'checkout_session_id': checkout_session.id,
                    'last_payment_date': datetime.now().timestamp()
                }
            )

        elif event.type == 'customer.subscription.created':
            subscription = event.data.object
            customer = stripe.Customer.retrieve(subscription.customer)
            
            # Get the plan details
            plan = subscription.items.data[0].price
            upload_credits = (
                10 if plan.product == 'basic' else
                50 if plan.product == 'premium' else
                'unlimited'
            )

            stripe.Customer.modify(
                customer.id,
                metadata={
                    'subscription_status': 'active',
                    'current_plan': plan.product,
                    'subscription_end_date': subscription.current_period_end,
                    'upload_credits': upload_credits,
                    'last_payment_date': datetime.now().timestamp(),
                    'subscription_id': subscription.id
                }
            )

        elif event.type == 'invoice.payment_succeeded':
            invoice = event.data.object
            customer = stripe.Customer.retrieve(invoice.customer)
            
            stripe.Customer.modify(
                customer.id,
                metadata={
                    'last_payment_date': datetime.now().timestamp()
                }
            )

        elif event.type == 'invoice.payment_failed':
            invoice = event.data.object
            customer = stripe.Customer.retrieve(invoice.customer)
            
            stripe.Customer.modify(
                customer.id,
                metadata={
                    'subscription_status': 'failed'
                }
            )

        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            customer = stripe.Customer.retrieve(subscription.customer)
            
            stripe.Customer.modify(
                customer.id,
                metadata={
                    'subscription_status': 'cancelled',
                    'current_plan': None
                }
            )

        return jsonify({'status': 'success'})
    except stripe.error.StripeError as e:
        print(f"Stripe API error: {str(e)}")
        return jsonify(error='Stripe API error', details=str(e)), 400
    except Exception as e:
        print(f"Unexpected error in webhook: {str(e)}")
        return jsonify(error='Internal server error', details=str(e)), 500


@subscription_bp.route('/subscription/status')
@login_required
@verify_account
def subscription_status():
    try:
        # Get user email from session
        user_email = session['user'].get('email')
        if not user_email:
            return jsonify({
                'error': 'User email not found in session',
                'status': 'error'
            }), 400

        # Get customer
        customer = stripe.Customer.list(email=user_email).data
        if not customer:
            return jsonify({
                'status': 'inactive',
                'error': 'Customer not found',
                'current_plan': None,
                'next_billing_date': None,
                'upload_credits': 0,
                'last_payment_date': None
            })

        customer = customer[0]
        metadata = customer.metadata
        
        # Get current subscription if exists
        subscriptions = stripe.Subscription.list(customer=customer.id)
        current_subscription = subscriptions.data[0] if subscriptions.data else None
        
        # Get payment history
        payments = stripe.PaymentIntent.list(customer=customer.id)
        
        return jsonify({
            'status': metadata.get('subscription_status', 'no_subscription'),
            'current_plan': metadata.get('current_plan', None),
            'next_billing_date': current_subscription.current_period_end if current_subscription else None,
            'upload_credits': metadata.get('upload_credits', 0),
            'last_payment_date': metadata.get('last_payment_date', None),
            'payments': [
                {
                    'id': payment.id,
                    'amount': payment.amount,
                    'created': payment.created,
                    'status': payment.status,
                    'invoice_url': payment.invoice
                }
                for payment in payments.data
            ]
        })

    except stripe.error.StripeError as e:
        print(f"Stripe API error getting subscription status: {str(e)}")
        return jsonify({
            'error': 'Stripe API error',
            'message': str(e),
            'status': 'error'
        }), 500

    except Exception as e:
        print(f"Error getting subscription status: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }), 500

@subscription_bp.route('/subscription/change-plan')
@login_required
@verify_account
def change_plan():
    try:
        user_email = session['user'].get('email')
        if not user_email:
            return jsonify({'error': 'User email not found'}), 400

        # Get customer
        customer = stripe.Customer.list(email=user_email).data[0]
        
        # Create checkout session for plan change
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': os.getenv('STRIPE_PRICE_ID_BASIC'),  # Make sure this is set in your .env
                'quantity': 1,
            }],
            success_url=url_for('subscription.manage_membership', _external=True) + '?success=true',
            cancel_url=url_for('subscription.manage_membership', _external=True) + '?cancelled=true',
            metadata={'user_id': session['user']['user_id']}
        )

        return jsonify({'url': checkout_session.url})

    except Exception as e:
        print(f"Error creating plan change session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription/payment-history')
@login_required
@verify_account
def payment_history():
    try:
        user_email = session['user'].get('email')
        if not user_email:
            return jsonify({'error': 'User email not found'}), 400

        # Get customer
        customer = stripe.Customer.list(email=user_email).data[0]
        
        # Get payment history
        payments = stripe.PaymentIntent.list(customer=customer.id)
        
        return jsonify({
            'payments': [
                {
                    'id': payment.id,
                    'amount': payment.amount,
                    'created': payment.created,
                    'status': payment.status,
                    'invoice_url': payment.invoice
                }
                for payment in payments.data
            ]
        })

    except Exception as e:
        print(f"Error getting payment history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription/cancel', methods=['POST'])
@login_required
@verify_account
def cancel_subscription():
    try:
        user_email = session['user'].get('email')
        if not user_email:
            return jsonify({'error': 'User email not found'}), 400

        # Get customer
        customer = stripe.Customer.list(email=user_email).data
        if not customer:
            return jsonify({'error': 'Customer not found'}), 400

        customer = customer[0]
        
        # Get active subscription
        subscriptions = stripe.Subscription.list(customer=customer.id, status='active')
        if not subscriptions.data:
            return jsonify({'error': 'No active subscription found'}), 400

        subscription = subscriptions.data[0]
        
        # Cancel subscription at period end
        cancelled_subscription = stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True
        )

        # Update customer metadata
        stripe.Customer.modify(
            customer.id,
            metadata={
                'subscription_status': 'cancelled_at_end',
                'current_plan': None
            }
        )

        return jsonify({
            'status': 'success',
            'message': 'Subscription will be cancelled at the end of the current billing cycle'
        })

    except stripe.error.StripeError as e:
        print(f"Stripe API error cancelling subscription: {str(e)}")
        return jsonify({
            'error': 'Stripe API error',
            'message': str(e)
        }), 500

    except Exception as e:
        print(f"Error cancelling subscription: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@subscription_bp.route('/manage-membership')
@login_required
@verify_account
def manage_membership():
    return render_template('dashboard/manage_membership.html')

@subscription_bp.route('/subscription/create', methods=['POST'])
def create_subscription():
    try:
        print("\n=== SUBSCRIPTION CREATION START ===")
        print(f"Request data: {request.json}")
        print(f"Session data: {dict(session)}")
        
        # Get plan ID from request
        plan_id = request.json.get('plan_id')
        print(f"Received plan_id: {plan_id}")
        
        if not plan_id:
            print("Error: Plan ID is missing")
            return jsonify({'error': 'Plan ID is required'}), 400

        # Get user data from session
        user_data = session.get('pending_user_data')
        print(f"Retrieved user_data from session: {user_data}")
        
        if not user_data:
            print("Error: User data not found in session")
            return jsonify({'error': 'User data not found in session'}), 400

        # Create or retrieve Stripe customer
        print(f"Attempting to find existing customer for email: {user_data['email']}")
        try:
            # Try to get existing customer
            customers = stripe.Customer.list(email=user_data['email'])
            print(f"Found {len(customers.data)} customers with this email")
            
            if customers.data:
                customer = customers.data[0]
                print(f"Found existing customer: {customer.id}")
            else:
                print("No existing customer found, creating new one...")
                # Create new customer
                customer = stripe.Customer.create(
                    email=user_data['email'],
                    name=user_data['name'],
                    phone=user_data['phone_number'],
                    metadata={
                        'cognito_user_id': user_data['cognito_user_id'],
                        'username': user_data['username']
                    }
                )
                print(f"Created new customer: {customer.id}")
                print(f"Customer metadata: {customer.metadata}")

        except Exception as e:
            print(f"Error retrieving/creating customer: {str(e)}")
            raise

        # Create subscription
        print(f"Creating subscription for customer: {customer.id}")
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': plan_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )
        print(f"Created subscription: {subscription.id}")
        print(f"Subscription status: {subscription.status}")

        # Update session with subscription status
        print("Updating session with subscription info")
        session['user']['subscription_status'] = 'pending'
        session['user']['subscription_id'] = subscription.id
        print(f"Updated session: {dict(session)}")

        print("=== SUBSCRIPTION CREATION SUCCESS ===")
        return jsonify({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        })

    except Exception as e:
        print(f"=== SUBSCRIPTION CREATION ERROR ===")
        print(f"Error creating subscription: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        print(f"Session state at error: {dict(session)}")
        return jsonify({'error': 'Failed to create subscription'}), 500
