from flask import session
import base64
import hashlib
import hmac

def calculate_password_claim_signature(username, password, user_id_for_srp, srp_b, salt, secret_block, client_id):
    """Calculate the password claim signature for SRP."""
    # Convert inputs to bytes
    username_bytes = username.encode('utf-8')
    password_bytes = password.encode('utf-8')
    user_id_bytes = user_id_for_srp.encode('utf-8')
    srp_b_bytes = srp_b.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    secret_block_bytes = secret_block.encode('utf-8')
    client_id_bytes = client_id.encode('utf-8')
    
    # Create the message
    message = hashlib.sha256()
    message.update(username_bytes)
    message.update(user_id_bytes)
    message.update(srp_b_bytes)
    message.update(salt_bytes)
    message.update(secret_block_bytes)
    message.update(client_id_bytes)
    message.update(password_bytes)
    
    # Create the signature
    signature = hmac.new(
        key=password_bytes,
        msg=message.digest(),
        digestmod=hashlib.sha256
    ).digest()
    
    return base64.b64encode(signature).decode('utf-8')


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
