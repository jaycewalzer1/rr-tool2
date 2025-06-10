from flask import session
import base64
import hashlib
import hmac

def cleanup_session():
    # Remove any unnecessary session data
    if 'auth' in session:
        # Keep only essential auth tokens
        session['auth'] = {
            'id_token': session['auth'].get('id_token'),
            'refresh_token': session['auth'].get('refresh_token'),
            'access_token': session['auth'].get('access_token')
        }
    
    if 'user' in session:
        # Keep only essential user info
        session['user'] = {
            'email': session['user'].get('email'),
            'username': session['user'].get('username'),
            'user_id': session['user'].get('user_id')
        }