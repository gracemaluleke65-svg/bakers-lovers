import os

# Set environment variables
os.environ['SECRET_KEY'] = '4e1e7c2419cfe3c3aa44f240ea356a40'
os.environ['DATABASE_URL'] = 'postgresql://bakerslovers:ymTgQWC57PTko8iD1Kg1iE9xQKfIyna5@dpg-d5r6faf5r7bs7390vel0-a.virginia-postgres.render.com/bakerslovers'
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Alter the password_hash column to increase size
    with db.engine.connect() as conn:
        conn.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(256)'))
        conn.commit()
        print("✅ Password field size increased to 256 characters")
    
    print("\nNow you can run fix_admin.py to update the admin password")