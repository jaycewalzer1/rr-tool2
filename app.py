from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_from_directory
from forms import LoginForm, SignupForm, ResetPasswordForm, ConfirmForm, ResetCodeForm, ConfirmResetForm, NewPasswordForm
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
from routes import register_routes
import os
from flask_session import Session


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
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

db.init_app(app)

UPLOAD_FOLDER = 'uploaded_pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

Session(app)


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

db.init_app(app)

register_routes(app)

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
