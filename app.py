from flask import Flask, request
from dotenv import load_dotenv
from models import db
from routes import register_routes
from flask_session import Session
from sqlalchemy import inspect
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timedelta
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# --- Flask Config ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Session Config ---
app.config['SESSION_TYPE'] = 'filesystem'                    # You can use 'redis' in production
app.config['SESSION_PERMANENT'] = True                       # Persistent sessions
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) # Cookie lives for 7 days
app.config['SESSION_COOKIE_SECURE'] = True                   # Only sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True                 # Not accessible via JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'                # Good CSRF protection with compatibility

# --- Initialize session and database ---
Session(app)
db.init_app(app)

# --- Trust proxy headers (for HTTPS detection behind ALB, NGINX, etc.) ---
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# --- Force HTTPS detection based on proxy headers ---
@app.before_request
def detect_https():
    if request.headers.get('X-Forwarded-Proto', 'http') == 'https':
        request.environ['wsgi.url_scheme'] = 'https'

# --- Register routes ---
register_routes(app)

# --- Run the app ---
if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)
        # Automatically create tables if they don't exist
        for table in ['user', 'file']:
            if not inspector.has_table(table):
                print(f"Creating {table} table...")
                db.create_all()

    # Development only — use Gunicorn or uWSGI in production
    app.run(host='0.0.0.0', port=5000, debug=True)
