from airtable import read_excel_from_s3
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, send_file, session, abort
from models import User, db
from decorators import verify_account, login_required
import stripe
import os
from datetime import datetime
import boto3
import botocore
import tempfile
from db_handler import process_uploaded_pdf

s3_client = boto3.client('s3')
excel_bucket = os.getenv('S3_BUCKET_NAME_EXCEL')

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
@verify_account
def dashboard():
    return render_template('dashboard/files.html')

@dashboard_bp.route('/database')
@login_required
@verify_account
def database():
    user_id = session.get('user', {}).get('user_id')
    username = session.get('user', {}).get('username')
    user_prefix = username.split('@')[0] if username else 'default'
    excel_key = f"uploads/{user_prefix}_master.xlsx"

    # Default values
    excel_file = None
    table_html = None

    # Check if Excel file exists, and load + render it
    try:
        s3_client.head_object(Bucket=excel_bucket, Key=excel_key)
        excel_file = f"{user_prefix}_master.xlsx"
        df = read_excel_from_s3(user_prefix)
        df.dropna(how="all", inplace=True)
        table_html = df.to_html(classes="table table-striped table-bordered", index=False)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] not in ['404', 'NoSuchKey']:
            raise
    except Exception as e:
        print(f"Error reading Excel for user {user_prefix}: {e}")

    # Get list of uploaded PDFs
    pdf_prefix = f"uploads/{user_id}/"
    response = s3_client.list_objects_v2(Bucket=os.getenv('S3_BUCKET_NAME_PDF'), Prefix=pdf_prefix)
    pdf_list = [obj['Key'].split('/')[-1] for obj in response.get('Contents', []) if obj['Key'].endswith('.pdf')]

    return render_template(
        'dashboard/database.html',
        excel_file=excel_file,
        pdf_list=pdf_list,
        table_html=table_html
    )

@dashboard_bp.route('/gmaps')
@login_required
@verify_account
def gmaps():
    return render_template(
        'dashboard/gmaps.html',
        GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY")  # or use current_app.config["GOOGLE_MAPS_API_KEY"]
    )

@dashboard_bp.route('/subscription/status')
def subscription_status():
    try:
        # Get user email from session
        user_email = session['user'].get('email')
        if not user_email:
            return jsonify(error="User email not found in session"), 400
            
        # Get customer data
        customers = stripe.Customer.list(email=user_email).data
        if not customers:
            return jsonify({
                'status': 'no_subscription',
                'current_plan': None,
                'next_billing_date': None,
                'upload_credits': 0,
                'last_payment_date': None
            })
            
        customer = customers[0]
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
                    'status': payment.status
                }
                for payment in payments.data
            ]
        })
    except Exception as e:
        print(f"Error in subscription status: {str(e)}")
        return jsonify(error=str(e)), 500

@dashboard_bp.route('/payment/history')
def payment_history():
    try:
        # Get user email from session
        user_email = session['user'].get('email')
        if not user_email:
            return jsonify(error="User email not found in session"), 400
            
        customer = stripe.Customer.list(email=user_email).data[0]
        payments = stripe.PaymentIntent.list(customer=customer.id)
        
        return jsonify({
            'payments': [
                {
                    'id': payment.id,
                    'amount': payment.amount,
                    'created': payment.created,
                    'status': payment.status
                }
                for payment in payments.data
            ]
        })
    except IndexError:
        return jsonify(error="Customer not found"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

@dashboard_bp.route('/create-checkout-session/<plan>', methods=['POST'])
@login_required
@verify_account
def create_checkout_session(plan):
    print("\n=== START CHECKOUT SESSION CREATION ===")
    print(f"Received request for plan: {plan}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request is JSON: {request.is_json}")
    
    # Ensure we're getting JSON
    if not request.is_json:
        print("Error: Request is not JSON")
        return jsonify({ 'error': 'Expected JSON request' }), 400

    try:
        print("\n=== USER SESSION CHECK ===")
        user_email = session.get('user', {}).get('email')
        user_id = session.get('user', {}).get('user_id')
        print(f"User info - email: {user_email}, id: {user_id}")
        print(f"Full session data: {dict(session)}")

        if not user_email or not user_id:
            print("Error: Missing user info")
            return jsonify({ 'error': 'User information not found in session' }), 400

        print("\n=== CUSTOMER MANAGEMENT ===")
        customer_list = stripe.Customer.list(email=user_email).data
        if customer_list:
            customer_id = customer_list[0].id
            print(f"Found existing customer: {customer_id}")
        else:
            print(f"Creating new customer for email: {user_email}")
            new_customer = stripe.Customer.create(
                email=user_email,
                metadata={
                    'subscription_status': 'pending',
                    'last_payment_date': datetime.now().isoformat(),
                    'user_id': user_id,
                    'current_plan': plan
                }
            )
            customer_id = new_customer.id
            print(f"Created new customer: {customer_id}")

        print("\n=== PLAN VALIDATION ===")
        plans = {
            'basic': {
                'name': 'Basic Plan',
                'amount': 999
            },
            'premium': {
                'name': 'Premium Plan',
                'amount': 2999
            },
            'enterprise': {
                'name': 'Enterprise Plan',
                'amount': 9999
            }
        }

        if plan not in plans:
            print(f"Error: Invalid plan: {plan}")
            return jsonify({ 'error': 'Invalid plan' }), 400

        print("\n=== CHECKOUT SESSION CREATION ===")
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': plans[plan]['amount'],
                    'product_data': {
                        'name': plans[plan]['name'],
                        'description': f"{plans[plan]['name']} subscription"
                    },
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1
            }],
            mode='subscription',
            success_url=url_for('dashboard.subscription', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('dashboard.subscription', _external=True) + '?cancelled=true',
            metadata={
                'user_id': user_id,
                'plan': plan
            }
        )

        print("\n=== CHECKOUT SESSION SUCCESS ===")
        print(f"Created checkout session: {checkout_session.id}")
        print(f"Session URL: {checkout_session.url}")
        print(f"Session status: {checkout_session.status}")
        print(f"Session payment status: {checkout_session.payment_status}")
        print(f"Session mode: {checkout_session.mode}")
        print(f"Session metadata: {checkout_session.metadata}")

        return jsonify({
            'id': checkout_session.id,
            'url': checkout_session.url
        })

    except stripe.error.StripeError as e:
        print("\n=== STRIPE ERROR ===")
        print(f"Stripe API error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error code: {getattr(e, 'code', 'unknown')}")
        return jsonify({ 'error': str(e) }), 400

    except Exception as e:
        print("\n=== GENERAL ERROR ===")
        print(f"Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return jsonify({ 'error': 'An unexpected error occurred' }), 500
    
@dashboard_bp.route('/api/s3/upload-url', methods=['POST'])
@login_required
def generate_presigned_upload_url():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Missing filename'}), 400

    user_id = session.get('user').get('user_id')

    s3_client = boto3.client('s3')
    bucket = os.getenv('S3_BUCKET_NAME_PDF')

    key = f"uploads/{user_id}/{filename}"

    url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=3600
    )

    return jsonify({
        'upload_url': url,
        's3_key': key
    })

@dashboard_bp.route('/api/s3/files', methods=['GET'])
@login_required
def list_s3_files():
    s3 = boto3.client('s3')
    bucket = os.getenv('S3_BUCKET_NAME_PDF')
    user_id = session.get('user', {}).get('user_id')
    prefix = f'uploads/{user_id}/'

    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        files = []

        for obj in response.get('Contents', []):
            key = obj['Key']
            filename = key.split('/')[-1]

            # Generate presigned GET URL (view in new tab)
            presigned_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=3600  # 1 hour
            )
            files.append({
                'filename': filename,
                's3_key': key,
                'public_url': presigned_url,
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat()
            })

        return jsonify({'files': files})

    except Exception as e:
        print(f"Error listing files from S3: {str(e)}")
        return jsonify({'error': 'Could not list files'}), 500

@dashboard_bp.route('/api/s3/files', methods=['DELETE'])
@login_required
def delete_s3_file():
    data = request.get_json()
    s3_key = data.get('s3_key')
    user_id = session.get('user', {}).get('user_id')

    if not s3_key or not user_id:
        return jsonify({'error': 'Missing s3_key or user_id'}), 400

    try:
        # Verify that the file belongs to the current user
        if not s3_key.startswith(f'uploads/{user_id}/'):
            return jsonify({'error': 'Unauthorized file access'}), 403

        s3_client.delete_object(
            Bucket=os.getenv('S3_BUCKET_NAME_PDF'),
            Key=s3_key
        )

        return jsonify({'message': 'File deleted successfully'})

    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return jsonify({'error': 'Failed to delete file'}), 500

@dashboard_bp.route('/files')
@login_required
@verify_account
def files():
    return render_template('dashboard/files.html')

    
@dashboard_bp.route('/api/s3/files', methods=['POST'])
@login_required
def handle_uploaded_file():
    data = request.get_json()
    filename = data.get('filename')
    username = session.get('user', {}).get('username')
    user_prefix = username.split('@')[0] if username else 'default'

    if not filename or not user_prefix:
        return jsonify({'error': 'Missing filename or user_id'}), 400

    try:
        # Call your OCR + Excel logic here
        result = process_uploaded_pdf(user_prefix, filename)

        df = read_excel_from_s3(user_prefix)
        return jsonify({
            'message': 'File processed successfully',
            'excel_key': result['excel_s3_key']
        })
    except Exception as e:
        print(f"Error processing uploaded file: {e}")
        return jsonify({'error': 'Processing failed'}), 500

@dashboard_bp.route('/dashboard/download-excel/<filename>')
@login_required
def download_master_excel(filename):
    username = session.get('user').get('username')
    user_prefix = username.split('@')[0] if username else 'default'
    expected_filename = f"{user_prefix}_master.xlsx"

    if filename != expected_filename:
        abort(403)  #prevent access to other users' files

    excel_key = f"uploads/{filename}"

    # Create a temporary file to download to
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
        try:
            s3_client.download_file(excel_bucket, excel_key, temp_excel.name)
            return send_file(
                temp_excel.name,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                download_name=filename,
                as_attachment=True
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
                abort(404)
            else:
                raise

@dashboard_bp.route('/excel-preview')
@login_required
def excel_preview():
    username = session['user']['username']
    user_prefix = username.split('@')[0] if username else 'default'
    try:
        df = read_excel_from_s3(user_prefix)

        df.dropna(how='all', inplace=True)

        table_html = df.to_html(classes="table table-striped table-bordered", index=False)
        return render_template('dashboard/excel_preview.html', table_html=table_html)
    except Exception as e:
        return f"Failed to load Excel data: {str(e)}", 500
