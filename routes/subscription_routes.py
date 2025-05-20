from flask import Blueprint, jsonify, request, session, redirect, url_for, flash
import stripe
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from decorators import login_required, verify_account

load_dotenv()

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
        user_email = session.get('user', {}).get('email')
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
                'message': 'No customer account found for this email'
            }), 404
            
        customer_id = customer[0].id
        customer_data = stripe.Customer.retrieve(customer_id)
        metadata = customer_data.metadata or {}

        # Get subscriptions
        subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)
        subscription = None
        if subscriptions.data:
            subscription = subscriptions.data[0]
            plan = subscription.items.data[0].price
        else:
            # Check if there's a pending subscription
            if metadata.get('subscription_status') == 'pending':
                return jsonify({
                    'status': 'pending',
                    'message': 'Subscription is being processed',
                    'checkout_session_id': metadata.get('checkout_session_id'),
                    'customer_id': customer_id
                }), 200

        if not subscription:
            return jsonify({
                'status': 'inactive',
                'message': 'No active subscription found',
                'customer_id': customer_id
            }), 200

        return jsonify({
            'status': subscription.status,
            'current_period_end': subscription.current_period_end,
            'plan': {
                'id': plan.id,
                'nickname': plan.nickname,
                'amount': plan.unit_amount,
                'currency': plan.currency
            },
            'customer_id': customer_id,
            'upload_credits': metadata.get('upload_credits'),
            'subscription_id': metadata.get('subscription_id'),
            'subscription_status': metadata.get('subscription_status')
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


@subscription_bp.route('/subscription/create', methods=['POST'])
@login_required
@verify_account
def create_subscription():
    try:
        customer = stripe.Customer.list(email=session['email']).data[0]
        plan_id = request.json.get('plan_id')

        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400

        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': plan_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )

        return jsonify({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        })
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return jsonify({'error': str(e)}), 500


@subscription_bp.route('/subscription/cancel', methods=['POST'])
@login_required
@verify_account
def cancel_subscription():
    try:
        customer = stripe.Customer.list(email=session['email']).data[0]
        subscription_id = request.json.get('subscription_id')

        if not subscription_id:
            return jsonify({'error': 'Subscription ID is required'}), 400

        subscription = stripe.Subscription.delete(subscription_id)

        return jsonify({'status': subscription.status})
    except Exception as e:
        print(f"Error canceling subscription: {str(e)}")
        return jsonify({'error': str(e)}), 500