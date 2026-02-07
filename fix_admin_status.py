import os

# Set environment variables
os.environ['SECRET_KEY'] = '4e1e7c2419cfe3c3aa44f240ea356a40'
os.environ['DATABASE_URL'] = 'postgresql://bakerslovers:ymTgQWC57PTko8iD1Kg1iE9xQKfIyna5@dpg-d5r6faf5r7bs7390vel0-a.virginia-postgres.render.com/bakerslovers'
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(email='admin@bakerslovers.com').first()
    
    if admin:
        print(f"Found user: {admin.email}")
        print(f"Current is_admin status: {admin.is_admin}")
        print(f"Current password hash length: {len(admin.password_hash)}")
        
        # Force set is_admin to True
        admin.is_admin = True
        db.session.commit()
        
        print(f"\n✅ Updated is_admin to: {admin.is_admin}")
        print("Admin status confirmed!")
    else:
        print("❌ Admin user not found!")
        print("Creating new admin...")
        
        from werkzeug.security import generate_password_hash
        
        new_admin = User(
            email='admin@bakerslovers.com',
            password_hash=generate_password_hash('Admin@123'),
            first_name='Admin',
            last_name='User',
            phone_number='0123456789',
            id_number='1234567890123',
            is_admin=True  # Explicitly set to True
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ New admin created with is_admin=True")

    # Verify all users
    print("\n--- All Users ---")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, is_admin: {user.is_admin}")