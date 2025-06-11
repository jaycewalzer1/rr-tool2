from flask import Flask
from dotenv import load_dotenv
from models import db
from routes import register_routes
from flask_session import Session
from sqlalchemy import inspect
from werkzeug.middleware.proxy_fix import ProxyFix
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session config
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_SECURE'] = True         # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True       # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'      # Good CSRF protection with compatibility

# Initialize session + database
Session(app)
db.init_app(app)

# Fix reverse proxy issues (HTTPS via ALB, NGINX, Cloudflare, etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Register routes
register_routes(app)

# App entrypoint
if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)

        # Create tables if missing
        for table in ['user', 'file']:
            if not inspector.has_table(table):
                print(f"Creating {table} table...")
                db.create_all()

    # Run with Flask (for dev only — use Gunicorn for production)
    app.run(host='0.0.0.0', port=5000, debug=True)
