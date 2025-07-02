from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from forms import LoginForm, SignupForm, ResetPasswordForm, ConfirmForm, ConfirmResetForm, NewPasswordForm
from auth import authenticate, get_secret_hash
from auth import cognito, COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID
from utils import cleanup_session
import stripe
import traceback
import os


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/subscription')
def subscription():
    stripe_key = os.getenv('STRIPE_PUBLIC_KEY')
    
    if not stripe_key:
        print("❌ STRIPE_PUBLIC_KEY is missing")
        raise RuntimeError("STRIPE_PUBLIC_KEY is not set in environment")

    return render_template('account/subscription.html', publishable_key=stripe_key)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            success, auth_response = authenticate(email, password)
            if not success:
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('auth.login'))

            session['auth'] = {
                'access_token': auth_response['AccessToken']
            }

            session['user'] = {
                'email': email,
                'username': email
            }

            response = cognito.get_user(AccessToken=session['auth']['access_token'])
            user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            session['user']['user_id'] = user_data.get('sub', None)

            # Clean up temporary session data
            cleanup_session()

            if user_data.get('email_verified') != 'true':
                flash('Please verify your email address before proceeding.', 'warning')
                return redirect(url_for('auth.confirm_signup'))

            return render_template('dashboard/files.html')

        except cognito.exceptions.UserNotConfirmedException:
            flash('Your account is not confirmed. Please check your email for the confirmation code.', 'danger')
            return redirect(url_for('auth.confirm_signup'))

        except cognito.exceptions.NotAuthorizedException:
            flash('Your account is not confirmed. Please check your email for the confirmation code.', 'danger')
            return redirect(url_for('auth.confirm_signup'))

        except cognito.exceptions.UserNotFoundException:
            flash('Email not found. Please sign up first!', 'danger')
            return redirect(url_for('auth.signup'))

        except Exception as e:
            print(f"Unexpected login error: {str(e)}")
            flash('Login failed. Please try again later!', 'danger')

    return render_template('account/login.html', form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        phone_number = f"+1{form.phone_number.data}"
        password = form.password.data

        print(f"Signup attempt: Username={username}, Email={email}, Phone={phone_number}")
        print(f"Session before storing pending signup: {dict(session)}")

        # Just store data in session — no Cognito call yet
        session['pending_user_data'] = {
            'name': name,
            'username': username,
            'email': email,
            'phone_number': phone_number,
            'password': password
        }
        
        session['user'] = {
            'email': email,
            'username': username,
            'password': password,
            'phone_number': phone_number,
            'name': name
        }

        session.permanent = True
        session.modified = True

        print("Stored pending_user_data in session")
        return redirect(url_for('auth.subscription'))

    return render_template('account/signup.html', form=form)


@auth_bp.route('/confirm-signup', methods=['GET', 'POST'])
def confirm_signup():
    if not request.args.get('subscription_completed'):
        print("⚠️ Missing subscription_completed param, redirecting to /subscription")
        return redirect(url_for('auth.subscription'))

    if 'user' not in session or 'username' not in session['user']:
        print("⚠️ Missing user data in session, redirecting to signup")
        flash("Please sign up first", "warning")
        return redirect(url_for('auth.signup'))

    form = ConfirmForm()

    if form.validate_on_submit():
        username = session['user']['username']
        confirmation_code = form.confirmation_code.data

        print(f"\n=== START CONFIRM SIGNUP ===")
        print(f"Attempting confirmation for username: {username}")
        print(f"Using code: {confirmation_code}")

        try:
            secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
            print(f"Generated secret_hash for confirmation: {secret_hash}")

            response = cognito.confirm_sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=username,
                ConfirmationCode=confirmation_code,
                SecretHash=secret_hash
            )
            print(f"✅ Cognito confirm_sign_up response: {response}")

            # Clean up session
            session['user'].pop('password', None)
            cleanup_session()
            print("🧹 Cleaned up session after confirmation")

            flash('Account confirmed successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except cognito.exceptions.ExpiredCodeException as e:
            print(f"⚠️ ExpiredCodeException: {str(e)}")
            flash('The confirmation code has expired. Please request a new one.', 'warning')
        except cognito.exceptions.CodeMismatchException as e:
            print(f"⚠️ CodeMismatchException: {str(e)}")
            flash('Invalid confirmation code. Please try again.', 'danger')
        except cognito.exceptions.UserNotFoundException as e:
            print(f"⚠️ UserNotFoundException: {str(e)}")
            flash('User not found in Cognito.', 'danger')
        except cognito.exceptions.NotAuthorizedException as e:
            print(f"⚠️ NotAuthorizedException (maybe already confirmed): {str(e)}")
            flash('Your account may already be confirmed.', 'info')
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"❌ Unexpected error during confirmation: {str(e)}")
            print(f"Traceback:\n{tb}")
            flash(f"Error confirming account: {str(e)}", 'danger')

    print("Rendering confirm signup page")
    return render_template('account/confirm_signup.html', form=form)





@auth_bp.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            secret_hash = get_secret_hash(email, COGNITO_APP_CLIENT_ID)
            cognito.forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email,
                SecretHash=secret_hash
            )
            flash('Password reset code sent. Check your email.', 'info')
            session['reset_email'] = email
            return redirect(url_for('auth.confirm_reset'))

        except cognito.exceptions.UserNotFoundException:
            flash('User not found.', 'danger')
        except cognito.exceptions.LimitExceededException:
            flash('Too many reset attempts. Try again later.', 'danger')
        except Exception as e:
            print(f"Reset error: {str(e)}")
            flash('Error sending reset code.', 'danger')

    return render_template('account/reset_password.html', form=form)


@auth_bp.route('/confirm-reset', methods=['GET', 'POST'])
def confirm_reset():
    if 'reset_email' not in session:
        flash('Start a reset request first.', 'info')
        return redirect(url_for('auth.reset'))

    form = ConfirmResetForm()
    if form.validate_on_submit():
        session['reset_confirmation_code'] = form.confirmation_code.data
        flash('Code verified! Set new password.', 'success')
        return redirect(url_for('auth.new_password'))

    return render_template('account/confirm_reset.html', form=form)


@auth_bp.route('/new-password', methods=['GET', 'POST'])
def new_password():
    form = NewPasswordForm()
    email = session.get('reset_email')
    confirmation_code = session.get('reset_confirmation_code')

    if not email or not confirmation_code:
        flash('Reset session expired.', 'info')
        return redirect(url_for('auth.reset'))

    if form.validate_on_submit():
        try:
            secret_hash = get_secret_hash(email, COGNITO_APP_CLIENT_ID)
            cognito.confirm_forgot_password(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=form.password.data,
                SecretHash=secret_hash
            )

            session.pop('reset_email', None)
            session.pop('reset_confirmation_code', None)

            flash('Password reset successfully. Log in now.', 'success')
            return redirect(url_for('auth.login'))

        except cognito.exceptions.CodeMismatchException:
            flash('Invalid code. Request a new one.', 'danger')
        except cognito.exceptions.NotAuthorizedException:
            flash('Code expired. Start reset again.', 'danger')
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            flash('Password reset failed.', 'danger')

    return render_template('account/new_password.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('misc.home'))
    return render_template('account/confirm_logout.html')

@auth_bp.route('/resend-confirmation-code', methods=['POST'])
def resend_confirmation_code():
    try:
        username = session.get('user', {}).get('username')
        if not username:
            return jsonify({'error': 'User session missing'}), 400

        secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)

        cognito.resend_confirmation_code(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=username,
            SecretHash=secret_hash
        )

        return jsonify({'success': True}), 200

    except Exception as e:
        print("Resend code error:", str(e))
        return jsonify({'error': 'Failed to resend confirmation code'}), 500

