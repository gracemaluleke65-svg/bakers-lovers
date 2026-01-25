# check_users.py
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

# Create the app context
app = create_app()

with app.app_context():
    # Get all users
    users = User.query.all()
    
    print(f"Total users in database: {User.query.count()}")
    print("\nUser Details:")
    print("-" * 80)
    
    if users:
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.first_name} {user.last_name}")
            print(f"Admin: {user.is_admin}")
            print(f"Created: {user.created_at}")
            print("-" * 80)
    else:
        print("No users found in database!")