import os
from datetime import timedelta


class Config:
    # Database - Render provides DATABASE_URL
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    
    # Handle Render's PostgreSQL URL (starts with postgres://, needs postgresql://)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix for SQLAlchemy 1.4+ compatibility with Render's postgres:// URLs
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 300,
            'pool_pre_ping': True,
        }
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///bakerslovers.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_THRESHOLD = 100
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True  # Required for HTTPS on Render
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Stripe configuration - MUST be set in environment variables
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    
    # Upload configuration
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Please log in to access this page.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    
    # Application settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@bakerslovers.com')


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False