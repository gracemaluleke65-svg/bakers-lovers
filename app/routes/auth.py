from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        # Check ID number
        existing_id = User.query.filter_by(id_number=form.id_number.data).first()
        if existing_id:
            flash('ID number already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            id_number=form.id_number.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            user.last_login = datetime.utcnow()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/reset-admin')
def reset_admin():
    """Reset or create admin user"""
    from app.models import User
    from werkzeug.security import generate_password_hash
    import os
    
    admin_email = 'admin@bakerslovers.com'
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    
    try:
        # Try to find existing admin
        admin = User.query.filter_by(email=admin_email).first()
        
        if admin:
            # Update existing admin
            admin.password_hash = generate_password_hash(admin_password)
            admin.is_admin = True
            admin.first_name = admin.first_name or 'Admin'
            admin.last_name = admin.last_name or 'User'
            admin.phone_number = admin.phone_number or '0123456789'
            
            if not admin.id_number:
                admin.id_number = f'ADMIN{admin.id:08d}'
            
            db.session.commit()
            
            return f"""
            <h1>✅ Admin Updated Successfully!</h1>
            <p><strong>Email:</strong> {admin_email}</p>
            <p><strong>Password:</strong> {admin_password}</p>
            <p><a href="/auth/login">Go to Login</a></p>
            """
        else:
            # Create new admin with unique id_number
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            
            new_admin = User(
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                first_name='Admin',
                last_name='User',
                phone_number='0123456789',
                id_number=f'ADMIN{timestamp}',  # Guaranteed unique
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            
            return f"""
            <h1>✅ Admin Created Successfully!</h1>
            <p><strong>Email:</strong> {admin_email}</p>
            <p><strong>Password:</strong> {admin_password}</p>
            <p><strong>ID Number:</strong> ADMIN{timestamp}</p>
            <p><a href="/auth/login">Go to Login</a></p>
            """
            
    except Exception as e:
        db.session.rollback()
        return f"""
        <h1>❌ Error</h1>
        <p>{str(e)}</p>
        <p>Check the logs for details.</p>
        """, 500