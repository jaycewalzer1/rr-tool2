from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cognito_sub = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    stripe_customer_id = db.Column(db.String(100), unique=True)
    subscription_status = db.Column(db.String(20), default='inactive')
    subscription_end_date = db.Column(db.DateTime)
    
    files = db.relationship('File', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    s3_key = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    size_bytes = db.Column(db.Integer)
    content_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    
    user = db.relationship('User', backref=db.backref('files', lazy=True))
