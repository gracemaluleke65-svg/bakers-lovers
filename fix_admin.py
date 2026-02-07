import os

# Set environment variables BEFORE importing app
os.environ['SECRET_KEY'] = '4e1e7c2419cfe3c3aa44f240ea356a40'
os.environ['DATABASE_URL'] = 'postgresql://bakerslovers:ymTgQWC57PTko8iD1Kg1iE9xQKfIyna5@dpg-d5r6faf5r7bs7390vel0-a.virginia-postgres.render.com/bakerslovers'
os.environ['FLASK_ENV'] = 'production'

# NOW import after setting env vars
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import hashlib

app = create_app()

def short_hash(password):
    """Create a shorter hash that fits in 128 chars"""
    return generate_password_hash(password, method='pbkdf2:sha256:1000')

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@bakerslovers.com').first()
    
    if admin:
        print("Admin found. Updating password...")
        # Set new password with shorter hash
        new_password = 'Admin@123'
        admin.password_hash = short_hash(new_password)
        db.session.commit()
        print(f"✅ Admin password updated to: {new_password}")
    else:
        print("Creating new admin user...")
        admin_password = 'Admin@123'
        new_admin = User(
            email='admin@bakerslovers.com',
            password_hash=short_hash(admin_password),
            first_name='Admin',
            last_name='User',
            phone_number='0123456789',
            id_number='1234567890123',
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print(f"✅ New admin created with password: {admin_password}")
    
    print("\n🎉 Login credentials:")
    print("Email: admin@bakerslovers.com")
    print("Password: Admin@123")