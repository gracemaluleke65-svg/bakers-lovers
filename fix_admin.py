from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import os

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@bakerslovers.com').first()
    
    if admin:
        print("Admin found. Updating password...")
        # Set new password
        new_password = 'Admin@123'  # You can change this
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        print(f"Admin password updated to: {new_password}")
    else:
        print("Creating new admin user...")
        admin_password = 'Admin@123'  # You can change this
        new_admin = User(
            email='admin@bakerslovers.com',
            password_hash=generate_password_hash(admin_password),
            first_name='Admin',
            last_name='User',
            phone_number='0123456789',
            id_number='1234567890123',
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print(f"New admin created with password: {admin_password}")
    
    print("\nLogin credentials:")
    print("Email: admin@bakerslovers.com")
    print("Password: Admin@123")