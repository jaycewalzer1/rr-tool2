from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_from_directory
from forms import LoginForm, SignupForm, ResetPasswordForm, ConfirmForm, ResetCodeForm, ConfirmResetForm, NewPasswordForm
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_file, send_from_directory
from forms import LoginForm, SignupForm, ResetPasswordForm, ConfirmForm
from models import db, User, File
import os
from dotenv import load_dotenv
import jwt
from functools import wraps
from auth import authenticate, get_secret_hash
from auth import cognito, COGNITO_REGION, COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID
import base64
import hashlib
import hmac
import six
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import shutil
import tempfile
from sqlalchemy import inspect
from tenant_parser.exporter import export_rent_roll_data_with_ocr
from werkzeug.utils import secure_filename
from openpyxl import load_workbook


def calculate_password_claim_signature(username, password, user_id_for_srp, srp_b, salt, secret_block, client_id):
    # Convert inputs to bytes
    username_bytes = username.encode('utf-8')
    password_bytes = password.encode('utf-8')
    user_id_bytes = user_id_for_srp.encode('utf-8')
    client_id_bytes = client_id.encode('utf-8')
    
    # Create key
    key = hashlib.sha256(user_id_bytes + client_id_bytes).digest()
    
    # Create message
    message = username_bytes + secret_block.encode('utf-8')
    
    # Create signature
    signature = hmac.new(key, message, hashlib.sha256).digest()
    
    return base64.b64encode(signature).decode('utf-8')

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

UPLOAD_FOLDER = 'uploaded_pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Routes are now handled by the home blueprint

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_token' not in session or 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_account(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_token' not in session or 'user_id' not in session:
            return redirect(url_for('login'))
        
        try:
            # Try to get user info with current access token
            try:
                response = cognito.get_user(
                    AccessToken=session['access_token']
                )
                user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
                return f(*args, **kwargs)
            except cognito.exceptions.NotAuthorizedException:
                # If access token is invalid, try to refresh it
                try:
                    # Get the username from the session
                    username = session.get('username')
                    if not username:
                        return redirect(url_for('login'))

                    # Calculate secret hash
                    secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)

                    refresh_response = cognito.initiate_auth(
                        ClientId=COGNITO_APP_CLIENT_ID,
                        AuthFlow='REFRESH_TOKEN_AUTH',
                        AuthParameters={
                            'REFRESH_TOKEN': session['refresh_token'],
                            'SECRET_HASH': secret_hash
                        }
                    )
                    
                    # Update session with new tokens
                    session['id_token'] = refresh_response['AuthenticationResult']['IdToken']
                    session['access_token'] = refresh_response['AuthenticationResult']['AccessToken']

                    # Try to get user info again with new access token
                    response = cognito.get_user(
                        AccessToken=session['access_token']
                    )
                    user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
                except Exception as refresh_error:
                    print(f"Error refreshing token: {str(refresh_error)}")
                    return redirect(url_for('login'))
            
            # Check if user is verified
            if 'email_verified' not in user_data or user_data['email_verified'] != 'true':
                flash('Please verify your email address before proceeding.', 'warning')
                return redirect(url_for('confirm_signup'))
            
            return f(*args, **kwargs)
        except Exception as e:
            import traceback
            print("=== ERROR IN verify_account ===")
            print(f"Exception: {e}")
            print(traceback.format_exc())
            return redirect(url_for('login'))
    return decorated_function

@app.route('/dashboard')
@login_required
@verify_account
def dashboard():
    return render_template('dashboard/dashboard.html')

@app.route('/dashboard/marketing')
@login_required
@verify_account
def marketing():
    user_files = os.listdir(UPLOAD_FOLDER)
    uploaded_files = [f for f in user_files if f.endswith('.pdf')]
    return render_template('dashboard/marketing.html', uploaded_files=uploaded_files)


@app.route('/dashboard/marketing/upload', methods=['POST'])
@login_required
def upload_rent_roll():
    if 'pdf' not in request.files:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('marketing'))

    file = request.files['pdf']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('marketing'))

    filename = secure_filename(file.filename)
    user_email = session.get('user_id', 'anonymous')  # or use user's email if stored

    # Save PDF locally
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(pdf_path)

    # Construct Excel path
    safe_user = secure_filename(user_email)
    excel_path = os.path.join("master_database", f"{safe_user}_master_database.xlsx")

    # Run processing pipeline
    try:
        export_rent_roll_data_with_ocr(pdf_path, excel_path, generate_summary=True)

        if not os.path.exists(excel_path):
            flash("Failed to process PDF.", 'danger')
        return redirect(url_for('marketing'))

    except Exception as e:
        print(f"Error processing upload: {e}")
        flash("Error processing file.", 'danger')
        return redirect(url_for('marketing'))


@app.route('/uploads/<filename>')
@login_required
def serve_uploaded_pdf(filename):
    return send_from_directory('uploaded_pdfs', filename)


@app.route('/dashboard/database')
@login_required
@verify_account
def database():
    user_email = session.get('user_id', 'anonymous')
    safe_user = secure_filename(user_email)
    excel_file = f"{safe_user}_master_database.xlsx"
    excel_path = os.path.join("master_database", excel_file)

    rows = []
    headers = []
    if os.path.exists(excel_path):
        wb = load_workbook(excel_path)
        sheet = wb["Retail Tenants"]
        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i == 0:
                headers = row
            else:
                rows.append(row)

    pdf_list = [f for f in os.listdir("uploaded_pdfs") if f.endswith(".pdf")]

    return render_template("dashboard/database.html",
                           excel_file=excel_file if os.path.exists(excel_path) else None,
                           headers=headers,
                           rows=rows,
                           pdf_list=pdf_list)

@app.route('/download/master/<filename>')
@login_required
def download_master_excel(filename):
    return send_from_directory("master_database", filename, as_attachment=True)

@app.route('/dashboard/files')
@login_required
@verify_account
def files():
    return render_template('dashboard/files.html')

@app.route('/api/local/upload', methods=['POST'])
def upload_file():
    if 'id_token' not in session or 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    user_id = session['user_id']
    upload_dir = os.path.join('uploads', user_id)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    return jsonify({
        'success': True,
        'file_path': file_path,
        'filename': file.filename
    })

@app.route('/api/local/files', methods=['GET'])
def get_files():
    if 'id_token' not in session or 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    upload_dir = os.path.join('uploads', user_id)
    
    if not os.path.exists(upload_dir):
        return jsonify({'files': []})

    files = []
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                'filename': filename,
                'size_bytes': os.path.getsize(file_path),
                'upload_date': os.path.getctime(file_path)
            })

    return jsonify({'files': files})

@app.route('/api/local/delete/<filename>', methods=['DELETE'])
def delete_local_file(filename):
    if 'id_token' not in session or 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    file_path = os.path.join('uploads', user_id, filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    os.remove(file_path)
    return jsonify({'success': True})

    s3_key = request.json.get('s3_key')
    if not s3_key:
        return jsonify({'error': 'S3 key is required'}), 400

    user_id = session['user_id']
    if not delete_file_from_s3(s3_key):
        return jsonify({'error': 'Failed to delete file from S3'}), 500

    file = File.query.filter_by(user_id=user_id, s3_key=s3_key).first()
    if file:
        db.session.delete(file)
        db.session.commit()

    return jsonify({'message': 'File deleted successfully'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            success, auth_response = authenticate(username, password)
            if not success:
                flash('Invalid username or password.', 'danger')
                return redirect(url_for('login'))

            # Store authentication tokens and user info
            session['id_token'] = auth_response['IdToken']
            session['refresh_token'] = auth_response['RefreshToken']
            session['access_token'] = auth_response['AccessToken']
            session['username'] = username
            
            # Get user info from Cognito
            response = cognito.get_user(
                AccessToken=session['access_token']
            )
            user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            session['user_id'] = user_data.get('sub', -1)
            session['username'] = username

            # Clean up any old session data
            cleanup_session()

            # Check if user is verified
            if 'email_verified' not in user_data or user_data['email_verified'] != 'true':
                flash('Please verify your email address before proceeding.', 'warning')
                return redirect(url_for('confirm_signup'))

            # Store all tokens in session for verify_account decorator
            session['id_token'] = auth_response['IdToken']
            session['refresh_token'] = auth_response['RefreshToken']
            session['access_token'] = auth_response['AccessToken']
            session['username'] = username
            session['user_id'] = user_data.get('sub', -1)

            return redirect(url_for('dashboard'))

        except cognito.exceptions.UserNotConfirmedException:
            flash('Your account is not confirmed. Please check your email for the confirmation code.', 'danger')
            return redirect(url_for('confirm_signup'))

        except cognito.exceptions.NotAuthorizedException:
            flash('Invalid username or password!', 'danger')
            return render_template('account/login.html', form=form)

        except cognito.exceptions.UserNotFoundException:
            flash('User not found. Please sign up first!', 'danger')
            return redirect(url_for('signup'))

        except Exception as e:
            print(f"Unexpected login error: {str(e)}")
            flash('Login failed. Please try again later!', 'danger')
            return render_template('account/login.html', form=form)

    return render_template('account/login.html', form=form)

# Function to clean up session data
def cleanup_session():
    # Remove any unnecessary session data
    keys_to_remove = ['access_token', 'user_info', 'last_login', 'preferences']
    for key in keys_to_remove:
        if key in session:
            del session[key]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        phone_number = form.phone_number.data
        # Add +1 prefix to phone number
        phone_number = f"+1{phone_number}"
        password = form.password.data
        
        try:
            # Calculate secret hash with client_id
            secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
            
            response = cognito.sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'phone_number', 'Value': phone_number},
                    {'Name': 'name', 'Value': name},
                    {'Name': 'preferred_username', 'Value': username}
                ],
                SecretHash=secret_hash
            )
            flash('Account created successfully! Check your email for the confirmation code.', 'success')
            session['pending_confirmation_username'] = username
            session['pending_confirmation_password'] = password
            session['pending_confirmation_name'] = name  # Store name for later use
            return redirect(url_for('confirm_signup'))
        
        except cognito.exceptions.UsernameExistsException:
            flash('Username already exists!', 'danger')
            return render_template('account/signup.html', form=form)
        
        except cognito.exceptions.InvalidPasswordException:
            flash('Invalid password format.', 'danger')
            return render_template('account/signup.html', form=form)
        
        except Exception as e:
            print(f"Signup error: {str(e)}")
            flash('Signup failed. Please try again!', 'danger')
            return render_template('account/signup.html', form=form)
    
    return render_template('account/signup.html', form=form)

@app.route('/resend-confirmation-code', methods=['POST'])
def resend_confirmation_code():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': 'Username is required'}), 400

    try:
        # Calculate secret hash with client_id
        secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
        
        try:
            cognito.resend_confirmation_code(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=username,
                SecretHash=secret_hash
            )
            return jsonify({'success': True, 'message': 'Confirmation code has been resent'})
        except cognito.exceptions.UserNotFoundException:
            return jsonify({'success': False, 'message': 'User not found. Please sign up first.'}), 404
        except cognito.exceptions.TooManyRequestsException:
            return jsonify({'success': False, 'message': 'Too many requests. Please wait a few minutes before trying again.'}), 429
        except Exception as e:
            print(f"Error resending confirmation code: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred while resending the confirmation code. Please try again.'}), 500
    except Exception as e:
        print(f"Error resending confirmation code: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/confirm-signup', methods=['GET', 'POST'])
def confirm_signup():
    if 'pending_confirmation_username' not in session:
        flash('Please sign up first!', 'danger')
        return redirect(url_for('signup'))

    form = ConfirmForm()
    if form.validate_on_submit():
        confirmation_code = form.confirmation_code.data
        username = session['pending_confirmation_username']
        password = session['pending_confirmation_password']

        try:
            # First confirm the signup
            # Calculate secret hash with client_id
            secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
            
            try:
                cognito.confirm_sign_up(
                    ClientId=COGNITO_APP_CLIENT_ID,
                    Username=username,
                    ConfirmationCode=confirmation_code,
                    SecretHash=secret_hash
                )
                flash('Account confirmed successfully!', 'success')

                # Authenticate using ADMIN_NO_SRP_AUTH
                auth_response = cognito.admin_initiate_auth(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    ClientId=COGNITO_APP_CLIENT_ID,
                    AuthFlow='ADMIN_NO_SRP_AUTH',
                    AuthParameters={
                        'USERNAME': username,
                        'PASSWORD': password,
                        'SECRET_HASH': secret_hash
                    }
                )

                # Store essential session data immediately
                session['id_token'] = auth_response['AuthenticationResult']['IdToken']
                session['refresh_token'] = auth_response['AuthenticationResult']['RefreshToken']
                session['access_token'] = auth_response['AuthenticationResult']['AccessToken']
                session['user_id'] = auth_response['AuthenticationResult']['AccessToken']  # Use AccessToken as user_id
                session['username'] = username

                # Get user info from Cognito
                response = cognito.get_user(
                    AccessToken=session['access_token']
                )
                user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
                
                # Update user_id with actual value from Cognito
                session['user_id'] = user_data.get('sub', session['user_id'])

                # Clean up any old session data
                cleanup_session()
                
                flash('Account confirmed and logged in successfully!', 'success')
                return redirect(url_for('dashboard'))

            except cognito.exceptions.ExpiredCodeException:
                flash('The confirmation code has expired. Please request a new one.', 'warning')
                return render_template('account/confirm_signup.html', form=form)

            except cognito.exceptions.CodeMismatchException:
                flash('Invalid confirmation code. Please check your email for the correct code.', 'danger')
                return render_template('account/confirm_signup.html', form=form)

            except Exception as e:
                print(f"Authentication error: {str(e)}")
                flash('An error occurred during authentication. Please try again.', 'danger')
                return render_template('account/confirm_signup.html', form=form)
            user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            
            # Clean up any old session data
            cleanup_session()
            
            flash('Account confirmed and logged in successfully!', 'success')
            return redirect(url_for('dashboard'))

        except cognito.exceptions.UserNotFoundException:
            flash('User not found. Please sign up first!', 'danger')
            return redirect(url_for('signup'))

        except cognito.exceptions.CodeMismatchException:
            flash('Invalid confirmation code. Please try again.', 'danger')
            return render_template('account/confirm_signup.html', form=form)
        except Exception as e:
            print(f"Confirmation error: {str(e)}")
            flash('Confirmation failed. Please try again!', 'danger')
            return render_template('account/confirm_signup.html', form=form)

    return render_template('account/confirm_signup.html', form=form)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            # Calculate secret hash with client_id
            secret_hash = get_secret_hash(email, COGNITO_APP_CLIENT_ID)
            
            cognito.forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email,
                SecretHash=secret_hash
            )
            
            flash('Password reset code sent successfully! Please check your email.', 'info')
            session['reset_email'] = email
            return redirect(url_for('confirm_reset'))
        except cognito.exceptions.UserNotFoundException:
            flash('User not found. Please check your email address.', 'danger')
            return render_template('account/reset_password.html', form=form)
        except cognito.exceptions.LimitExceededException:
            flash('Too many reset attempts. Please wait a few minutes before trying again.', 'danger')
        except Exception as e:
            print(f"Reset error: {str(e)}")
            flash('Error sending reset code. Please try again!', 'danger')
            return render_template('account/reset_password.html', form=form)

    return render_template('account/reset_password.html', form=form)




@app.route('/confirm-reset', methods=['GET', 'POST'])
def confirm_reset():
    if 'reset_email' not in session:
        flash('Please request a password reset first. Check your email for the reset link.', 'info')
        return redirect(url_for('reset'))

    form = ConfirmResetForm()  # Includes confirmation code only
    if form.validate_on_submit():
        email = session['reset_email']
        confirmation_code = form.confirmation_code.data

        try:
            secret_hash = get_secret_hash(email, COGNITO_APP_CLIENT_ID)

            # Verify the confirmation code first
            try:
                cognito.admin_get_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=email
                )
                
                # Store the code in session
                session['reset_confirmation_code'] = confirmation_code
                flash('Confirmation code verified! Please set your new password.', 'success')
                return redirect(url_for('new_password'))
            except Exception as e:
                print(f"User verification error: {str(e)}")
                flash('Invalid confirmation code or user not found. Please check your email for the correct code.', 'danger')
                return render_template('account/confirm_reset.html', form=form)
            
            # Store the code in session and redirect to new_password
            session['reset_confirmation_code'] = confirmation_code
            flash('Confirmation code verified! Please set your new password.', 'success')
            return redirect(url_for('new_password'))

        except cognito.exceptions.CodeMismatchException as e:
            print(f"Code mismatch error: {str(e)}")
            flash('Invalid confirmation code. Please check your email for the correct code.', 'danger')
        except cognito.exceptions.NotAuthorizedException as e:
            print(f"Not authorized error: {str(e)}")
            flash('Password reset request has expired. Please request a new reset code.', 'danger')
        except Exception as e:
            print(f"Confirmation error: {str(e)}")
            flash('An error occurred while verifying your code. Please try again.', 'danger')

    return render_template('confirm_reset.html', form=form)

@app.route('/new-password', methods=['GET', 'POST'])
def new_password():
    form = NewPasswordForm()  # Includes new password and confirm password

    # Ensure reset flow has been initiated
    email = session.get('reset_email')
    confirmation_code = session.get('reset_confirmation_code')

    if not email or not confirmation_code:
        flash('Please request a password reset first. Check your email for the reset link.', 'info')
        return redirect(url_for('reset'))

    if form.validate_on_submit():
        try:
            email = email.strip()
            new_password = form.password.data
            secret_hash = get_secret_hash(email, COGNITO_APP_CLIENT_ID)

            print(f"Resetting password for {email}")
            response = cognito.confirm_forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password,
                SecretHash=secret_hash
            )
            print(f"Password reset response: {response}")

            # Clean up session
            session.pop('reset_email', None)
            session.pop('reset_confirmation_code', None)

            flash('Password has been successfully reset! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))

        except cognito.exceptions.CodeMismatchException:
            flash('Invalid confirmation code. Please request a new reset code.', 'danger')
        except cognito.exceptions.NotAuthorizedException:
            flash('The reset code has expired. Please request a new one.', 'danger')
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            flash('Password reset failed. Please try again.', 'danger')

    return render_template('account/new_password.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # Clear all session data
        session.clear()
        return redirect(url_for('home'))
    
    # For GET requests, show the confirmation page
    return render_template('account/confirm_logout.html')

@app.route("/contact")
def contact():
    return render_template("home/contact.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def home():
    return render_template('home/index.html')

@app.route('/solutions')
def solutions():
    return render_template('home/solutions.html')

@app.route('/company')
def company():
    return render_template('home/company.html')

@app.route('/platform')
def platform():
    return render_template('home/platform.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/privacy')
def privacy():
    return render_template('home/privacy.html')

@app.route('/terms')
def terms():
    return render_template('home/terms.html')

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()

        inspector = inspect(db.engine)
        
        # Check if tables exist
        if not inspector.has_table('user'):
            print("Creating user table...")
            db.create_all()
        
        if not inspector.has_table('file'):
            print("Creating file table...")
            db.create_all()
    
    app.run(host="0.0.0.0", port=8080, debug=True)
