from functools import wraps
from flask import session, redirect, flash, url_for
from auth import cognito, COGNITO_APP_CLIENT_ID
import os

COGNITO_REGION = os.getenv("AWS_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if we have the auth data
        if 'auth' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if we have the user data
        if 'user' not in session:
            flash('User session data is missing.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if we have essential tokens
        if not all(key in session['auth'] for key in ['id_token', 'refresh_token', 'access_token']):
            flash('Authentication data is missing.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if we have essential user info
        if not all(key in session['user'] for key in ['email', 'username', 'user_id']):
            flash('User data is missing.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def verify_account(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # First check if we have all required session data
            if not login_required(f)(*args, **kwargs):
                return redirect(url_for('auth.login'))
            
            # Try to get user info with current access token
            try:
                response = cognito.get_user(
                    AccessToken=session['auth']['access_token']
                )
                user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
                
                # Check if user is verified
                if 'email_verified' not in user_data or user_data['email_verified'] != 'true':
                    flash('Please verify your email address before proceeding.', 'warning')
                    return redirect(url_for('auth.confirm_signup'))
                
                return f(*args, **kwargs)
            except cognito.exceptions.NotAuthorizedException:
                # If access token is invalid, try to refresh it
                try:
                    # Get the username from the session
                    username = session['user'].get('username')
                    if not username:
                        return redirect(url_for('auth.login'))

                    # Calculate secret hash
                    secret_hash = get_secret_hash(username, COGNITO_APP_CLIENT_ID)

                    refresh_response = cognito.initiate_auth(
                        ClientId=COGNITO_APP_CLIENT_ID,
                        AuthFlow='REFRESH_TOKEN_AUTH',
                        AuthParameters={
                            'REFRESH_TOKEN': session['auth']['refresh_token'],
                            'SECRET_HASH': secret_hash
                        }
                    )
                    
                    # Update session with new tokens using the new structure
                    session['auth'] = {
                        'id_token': refresh_response['AuthenticationResult']['IdToken'],
                        'refresh_token': refresh_response['AuthenticationResult']['RefreshToken'],
                        'access_token': refresh_response['AuthenticationResult']['AccessToken']
                    }

                    # Try to get user info again with new access token
                    response = cognito.get_user(
                        AccessToken=session['auth']['access_token']
                    )
                    user_data = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
                    
                    # Check if user is verified
                    if 'email_verified' not in user_data or user_data['email_verified'] != 'true':
                        flash('Please verify your email address before proceeding.', 'warning')
                        return redirect(url_for('auth.confirm_signup'))
                except Exception as refresh_error:
                    print(f"Error refreshing token: {str(refresh_error)}")
                    return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Error verifying account: {str(e)}")
            return redirect(url_for('auth.login'))
    return decorated_function
