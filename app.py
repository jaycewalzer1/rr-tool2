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


@app.route('/')
def home():
    return render_template('index.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_token' not in session or 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_id') == -1:
        flash("You're in limited demo mode. Please confirm your account for full access.", 'warning')
    return render_template('dashboard.html')

@app.route('/dashboard/marketing')
@login_required
def marketing():
    user_files = os.listdir(UPLOAD_FOLDER)
    uploaded_files = [f for f in user_files if f.endswith('.pdf')]
    return render_template('marketing.html', uploaded_files=uploaded_files)


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

    return render_template("database.html",
                           excel_file=excel_file if os.path.exists(excel_path) else None,
                           headers=headers,
                           rows=rows,
                           pdf_list=pdf_list)

@app.route('/download/master/<filename>')
@login_required
def download_master_excel(filename):
    return send_from_directory("master_database", filename, as_attachment=True)

@app.route('/platform')
def platform():
    return render_template('platform.html')

@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

@app.route('/company')
def company():
    return render_template('404.html'), 404

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

            session['id_token'] = auth_response['IdToken']
            session['refresh_token'] = auth_response['RefreshToken']
            session['access_token'] = auth_response['AccessToken']

            user_info = cognito.get_user(AccessToken=session['access_token'])

            user_id = next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'sub'), None)

            if user_id:
                session['user_id'] = user_id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Failed to retrieve user information.', 'danger')
                return redirect(url_for('login'))

        except cognito.exceptions.UserNotConfirmedException:
            flash('Your account is not confirmed. Please check your email for the confirmation code.', 'warning')
            return redirect(url_for('login'))

        except cognito.exceptions.NotAuthorizedException:
            flash('Invalid username or password!', 'danger')
            return render_template('login.html', form=form)

        except cognito.exceptions.UserNotFoundException:
            flash('User not found. Please sign up first!', 'danger')
            return redirect(url_for('signup'))

        except Exception as e:
            print(f"Unexpected login error: {str(e)}")
            flash('Login failed. Please try again later!', 'danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data
        
        try:
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
                SecretHash=get_secret_hash(username)
            )
            flash('Account created successfully! Check your email for the confirmation code.', 'success')
            session['pending_confirmation_username'] = username
            session['pending_confirmation_password'] = password
            session['pending_confirmation_name'] = name  # Store name for later use
            return redirect(url_for('confirm_signup'))
        
        except cognito.exceptions.UsernameExistsException:
            flash('Username already exists!', 'danger')
            return render_template('signup.html', form=form)
        
        except cognito.exceptions.InvalidPasswordException:
            flash('Invalid password format.', 'danger')
            return render_template('signup.html', form=form)
        
        except Exception as e:
            print(f"Signup error: {str(e)}")
            flash('Signup failed. Please try again!', 'danger')
            return render_template('signup.html', form=form)
    
    return render_template('signup.html', form=form)

@app.route('/resend-confirmation-code', methods=['POST'])
def resend_confirmation_code():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': 'Username is required'}), 400
    
    try:
        cognito.resend_confirmation_code(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=username,
            SecretHash=get_secret_hash(username)
        )
        return jsonify({'success': True, 'message': 'Confirmation code has been resent'})
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
            cognito.confirm_sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=username,
                ConfirmationCode=confirmation_code,
                SecretHash=get_secret_hash(username)
            )

            # Authenticate using ADMIN_NO_SRP_AUTH
            auth_response = cognito.admin_initiate_auth(
                UserPoolId=COGNITO_USER_POOL_ID,
                ClientId=COGNITO_APP_CLIENT_ID,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': get_secret_hash(username)
                }
            )

            # Store tokens in session
            session['id_token'] = auth_response['AuthenticationResult']['IdToken']
            session['refresh_token'] = auth_response['AuthenticationResult']['RefreshToken']
            session['access_token'] = auth_response['AuthenticationResult']['AccessToken']

            # Get user info from Cognito
            user_info = cognito.get_user(
                AccessToken=session['access_token']
            )

            # Store user ID in session
            user_id = next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'sub'), None)
            if user_id:
                session['user_id'] = user_id
                flash('Account confirmed and logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Failed to retrieve user information.', 'danger')
                return redirect(url_for('login'))

        except cognito.exceptions.CodeMismatchException:
            flash('Invalid confirmation code. Please try again.', 'danger')
            return render_template('confirm_signup.html', form=form)
        except Exception as e:
            print(f"Confirmation error: {str(e)}")
            flash('Confirmation failed. Please try again!', 'danger')
            return render_template('confirm_signup.html', form=form)

    return render_template('confirm_signup.html', form=form)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            cognito.forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email
            )
            flash('Password reset code sent successfully! Please check your email.', 'info')
            session['reset_email'] = email
            return redirect(url_for('confirm_reset'))
        except cognito.exceptions.UserNotFoundException:
            flash('User not found. Please check your email address.', 'danger')
            return render_template('reset_password.html', form=form)
        except Exception as e:
            print(f"Reset error: {str(e)}")
            flash('Error sending reset code. Please try again!', 'danger')
            return render_template('reset_password.html', form=form)

    return render_template('reset_password.html', form=form)

@app.route('/confirm-reset', methods=['GET', 'POST'])
def confirm_reset():
    if 'reset_email' not in session:
        flash('Please request a password reset first!', 'danger')
        return redirect(url_for('reset'))

    form = ResetCodeForm()
    if form.validate_on_submit():
        confirmation_code = form.confirmation_code.data
        email = session['reset_email']
        
        try:
            # Verify the confirmation code
            cognito.confirm_forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code
            )
            
            # Store the email in session for the next step
            session['reset_email_confirmed'] = email
            
            flash('Confirmation code verified successfully!', 'success')
            return redirect(url_for('new_password'))
            
        except cognito.exceptions.CodeMismatchException:
            flash('Invalid confirmation code. Please try again.', 'danger')
            return render_template('confirm_reset.html', form=form)
        except Exception as e:
            print(f"Confirmation error: {str(e)}")
            flash('Confirmation failed. Please try again!', 'danger')
            return render_template('confirm_reset.html', form=form)

    return render_template('confirm_reset.html', form=form)

@app.route('/new-password', methods=['GET', 'POST'])
def new_password():
    if 'reset_email_confirmed' not in session:
        flash('Please confirm your reset code first!', 'danger')
        return redirect(url_for('reset'))

    form = NewPasswordForm()
    if form.validate_on_submit():
        email = session['reset_email_confirmed']
        new_password = form.password.data
        
        try:
            # Change the password
            cognito.confirm_forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email,
                Password=new_password,
                ConfirmationCode='confirmed'  # This is a placeholder since we've already confirmed
            )
            
            # Clear the session variables
            session.pop('reset_email', None)
            session.pop('reset_email_confirmed', None)
            
            flash('Password changed successfully! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Password change error: {str(e)}")
            flash('Error changing password. Please try again!', 'danger')
            return render_template('new_password.html', form=form)

    return render_template('new_password.html', form=form)
    if form.validate_on_submit():
        email = form.email.data
        try:
            cognito.forgot_password(ClientId=COGNITO_APP_CLIENT_ID, Username=email)
            flash('Password reset link sent successfully!', 'info')
            return redirect(url_for('login'))
        except cognito.exceptions.UserNotFoundException:
            flash('User not found. Please check your email.', 'danger')
            return redirect(url_for('reset'))
        except Exception as e:
            print(f"Reset error: {str(e)}")
            flash('Error sending reset link. Please try again!', 'danger')
            return redirect(url_for('reset'))

    return render_template('reset.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/contact")
def contact():
    return render_template("404.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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
