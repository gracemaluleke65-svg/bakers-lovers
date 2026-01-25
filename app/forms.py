# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
import re
from datetime import date  # FIXED: Added missing import


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    id_number = StringField('ID Number', validators=[DataRequired(), Length(min=13, max=13)])
    submit = SubmitField('Register')
    
    def validate_phone_number(self, phone_number):
        if not re.match(r'^0\d{9}$', phone_number.data):
            raise ValidationError('Phone number must start with 0 and be 10 digits')
    
    def validate_id_number(self, id_number):
        if not re.match(r'^\d{13}$', id_number.data):
            raise ValidationError('ID number must be 13 digits')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    category = SelectField('Category', choices=[
        ('Birthday', 'Birthday'), 
        ('Wedding', 'Wedding'), 
        ('Custom', 'Custom'),
        ('Corporate', 'Corporate')
    ], default='Birthday')
    size = SelectField('Size', choices=[
        ('6-inch', '6-inch'),
        ('8-inch', '8-inch'),
        ('10-inch', '10-inch'),
        ('12-inch', '12-inch'),
        ('2-Tier', '2-Tier'),
        ('3-Tier', '3-Tier'),
        ('4-Tier', '4-Tier')
    ], default='6-inch')
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    image_file = FileField('Product Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Save Product')


class CouponForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired(), Length(max=20)])
    discount_amount = DecimalField('Discount Amount', validators=[DataRequired(), NumberRange(min=0)], places=2)
    is_percentage = BooleanField('Is Percentage')
    valid_from = DateField('Valid From', validators=[DataRequired()], default=date.today)  # FIXED: date.today
    valid_to = DateField('Valid To', validators=[DataRequired()])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Save Coupon')
    
    def validate_valid_to(self, valid_to):
        if valid_to.data and self.valid_from.data:
            if valid_to.data < self.valid_from.data:
                raise ValidationError('Valid To date must be after Valid From date')


class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars')
    ], validators=[DataRequired()], coerce=int)
    # ... rest of the form
    

class OrderForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    total_amount = DecimalField('Total Amount', validators=[DataRequired(), NumberRange(min=0)], places=2)
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Baking', 'Baking'), 
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ])
    payment_status = SelectField('Payment Status', choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    ])
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(max=500)])
    stripe_session_id = StringField('Stripe Session ID', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save Order')