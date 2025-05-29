from flask import Flask
from dotenv import load_dotenv
from models import db
from routes import register_routes
import os
from flask_session import Session
from sqlalchemy import inspect

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

Session(app)

db.init_app(app)

register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)

        if not inspector.has_table('user'):
            print("Creating user table...")
            db.create_all()

        if not inspector.has_table('file'):
            print("Creating file table...")
            db.create_all()
    
    app.run(debug=True)