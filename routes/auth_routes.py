from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from forms import LoginForm, SignupForm, ResetPasswordForm, ConfirmForm, ConfirmResetForm, NewPasswordForm
from auth import authenticate, get_secret_hash
from auth import cognito, COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID
from utils import cleanup_session
import stripe
import traceback


auth_bp = Blueprint('auth', __name__)

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
        print(f"Session before Cognito signup: {dict(session)}")

        try:
            # Create Cognito user immediately
            secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
            print(f"Generated secret hash for user {username}")
            
            response = cognito.sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=username,
                Password=password,
                SecretHash=secret_hash,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'phone_number', 'Value': phone_number},
                    {'Name': 'name', 'Value': name},
                    {'Name': 'preferred_username', 'Value': username}
                ]
            )
            
            print(f"Cognito signup response: {response}")
            print(f"Cognito user ID: {response['UserSub']}")
            
           # Temporarily store signup form data
            session['pending_user_data'] = {
                'name': name,
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'password': password,
                'cognito_user_id': response['UserSub']
            }
            
            # Redirect to payment setup
            return redirect(url_for('misc.create_checkout_session', plan_id='basic'))


        except cognito.exceptions.UsernameExistsException:
            print(f"Username {username} already exists")
            flash('Username already exists. Please choose a different one.', 'danger')
        except cognito.exceptions.InvalidParameterException as e:
            print(f"Invalid parameter error: {str(e)}")
            flash('Invalid signup parameters. Please check your input and try again.', 'danger')
        except Exception as e:
            print(f"Signup error: {str(e)}")
            print(f"Full traceback: {traceback.format_exc()}")
            flash('Error creating account. Please try again.', 'danger')

    return render_template('account/signup.html', form=form)


@auth_bp.route('/resend-confirmation-code', methods=['POST'])
def resend_confirmation_code():
    username = session.get('pending_confirmation_username')
    if not username:
        flash('Please sign up first!', 'danger')
        return redirect(url_for('auth.signup'))

    try:
        secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
        cognito.resend_confirmation_code(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=username,
            SecretHash=secret_hash
        )
        flash('Confirmation code has been resent to your email.', 'success')
    except Exception as e:
        flash(f'Error resending confirmation code: {str(e)}', 'danger')

    return redirect(url_for('auth.confirm_signup'))


@auth_bp.route('/confirm-signup', methods=['GET', 'POST'])
def confirm_signup():
    # Check if user has completed subscription
    if request.args.get('subscription_completed'):
        session['subscription_completed'] = True
    elif 'subscription_completed' not in session or not session['subscription_completed']:
        flash('Please complete your subscription first!', 'warning')
        return redirect(url_for('dashboard.subscription'))

    if 'pending_user_data' not in session:
        flash('Please sign up first!', 'danger')
        return redirect(url_for('auth.signup'))

    form = ConfirmForm()
    if form.validate_on_submit():
        username = session['pending_user_data']['username']
        confirmation_code = form.confirmation_code.data
        
        try:
            secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)
            cognito.confirm_sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=username,
                ConfirmationCode=confirmation_code,
                SecretHash=secret_hash
            )

            # Authenticate the user
            auth_response = cognito.initiate_auth(
                ClientId=COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': session['pending_user_data']['password'],
                    'SECRET_HASH': secret_hash
                }
            )

            # Set up session
            session['auth'] = {
                'access_token': auth_response['AuthenticationResult']['AccessToken'],
                'refresh_token': auth_response['AuthenticationResult']['RefreshToken'],
                'id_token': auth_response['AuthenticationResult']['IdToken']
            }

            # Get user info
            response = cognito.get_user(AccessToken=session['auth']['access_token'])
            user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            
            session['user'] = {
                'email': user_data.get('email', ''),
                'username': user_data.get('username', ''),
                'user_id': user_data.get('sub', '')
            }

            # Clean up temporary data
            cleanup_session()

            flash('Account confirmed and logged in successfully!', 'success')
            return redirect(url_for('auth.login'))

        except cognito.exceptions.ExpiredCodeException:
            flash('The confirmation code has expired.', 'warning')
        except cognito.exceptions.CodeMismatchException:
            flash('Invalid confirmation code.', 'danger')
        except Exception as e:
            print(f"Confirmation error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')

    # If GET request or form validation failed, show the form
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
