import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pythonanywhere_secret_key_2025_05_05')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
