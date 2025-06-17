print("🔧 Importing standard libraries...")
from datetime import timedelta
import os

print("🔧 Importing Flask and extensions...")
from flask import Flask, request
from dotenv import load_dotenv
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

print("🔧 Importing SQLAlchemy and models...")
from sqlalchemy import inspect
from models import db

print("🔧 Importing routes...")
from routes import register_routes

# Load environment variables
print("📦 Loading environment variables...")
load_dotenv()

# Initialize Flask app
print("🚀 Initializing Flask app...")
app = Flask(__name__)

# --- Flask Config ---
print("⚙️ Setting Flask config...")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Session Config ---
print("⚙️ Setting session config...")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

# --- Initialize session and database ---
print("📦 Initializing session and db...")
Session(app)
db.init_app(app)

# --- Trust proxy headers ---
print("📡 Applying ProxyFix middleware...")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# --- HTTPS detection ---
@app.before_request
def detect_https():
    if request.headers.get('X-Forwarded-Proto', 'http') == 'https':
        request.environ['wsgi.url_scheme'] = 'https'

# --- Register routes ---
print("🛣️ Registering routes...")
register_routes(app)

# --- Run the app ---
if __name__ == '__main__':
    print("🧠 Entering app context...")
    with app.app_context():
        inspector = inspect(db.engine)
        for table in ['user', 'file']:
            if not inspector.has_table(table):
                print(f"🛠️ Creating {table} table...")
                db.create_all()
    print("✅ App setup complete. Launching server...")

    app.run(host='0.0.0.0', port=5000, debug=True)