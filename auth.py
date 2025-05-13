import boto3
from flask import session
import os
from dotenv import load_dotenv
import hmac
import hashlib
import base64

# Load environment variables
load_dotenv()

# Required environment variables
REQUIRED_ENV_VARS = [
    "AWS_REGION",
    "COGNITO_USER_POOL_ID",
    "COGNITO_APP_CLIENT_ID",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "COGNITO_APP_CLIENT_SECRET"
]

# Validate environment variables
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

COGNITO_REGION = os.getenv("AWS_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
COGNITO_APP_CLIENT_SECRET = os.getenv("COGNITO_APP_CLIENT_SECRET")

# Configure AWS credentials
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=COGNITO_REGION
)

cognito = boto3.client('cognito-idp')

def get_secret_hash(username):
    msg = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(COGNITO_APP_CLIENT_SECRET.encode('utf-8'), 
                   msg = msg.encode('utf-8'),
                   digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

def authenticate(username, password):
    try:
        resp = cognito.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username, 
                'PASSWORD': password,
                'SECRET_HASH': get_secret_hash(username)
            }
        )
        session['id_token'] = resp['AuthenticationResult']['IdToken']
        return True, resp['AuthenticationResult']
    except cognito.exceptions.NotAuthorizedException:
        return False, None