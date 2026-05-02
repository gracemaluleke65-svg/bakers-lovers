from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db

class BKL_User(UserMixin, db.Model):
    __tablename__ = 'bkl_user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    id_number = db.Column(db.String(13), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    orders = db.relationship('BKL_Order', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('BKL_Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('BKL_Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.id)
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<BKL_User {self.email}>'


class BKL_Product(db.Model):
    __tablename__ = 'bkl_product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default='')
    category = db.Column(db.String(100), default='Birthday')
    size = db.Column(db.String(50), default='6-inch')
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    image_bytes = db.Column(db.LargeBinary, nullable=True)
    available = db.Column(db.Boolean, default=True)
    
    # Relationships
    order_items = db.relationship('BKL_OrderItem', backref='product', lazy=True)
    favorites = db.relationship('BKL_Favorite', backref='product', lazy=True)
    cart_items = db.relationship('BKL_CartItem', backref='product', lazy=True)


class BKL_CartItem(db.Model):
    __tablename__ = 'bkl_cart_item'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('bkl_product.id'), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BKL_Cart:
    def __init__(self, session_id=None):
        self.items = []
        self.session_id = session_id
        if not self.session_id:
            from flask import session
            self.session_id = session.get('cart_id')
        if not self.session_id:
            import datetime
            self.session_id = str(datetime.datetime.utcnow().timestamp())
            session['cart_id'] = self.session_id
        self.load_from_db()
    
    def add_item(self, product, quantity=1):
        existing_item = next((item for item in self.items if item.product_id == product.id), None)
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = BKL_CartItem(
                session_id=self.session_id,
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=quantity
            )
            self.items.append(cart_item)
    
    def update_item(self, product_id, quantity):
        item = next((item for item in self.items if item.product_id == product_id), None)
        if item:
            if quantity > 0:
                item.quantity = quantity
                db_item = BKL_CartItem.query.filter_by(
                    session_id=self.session_id,
                    product_id=product_id
                ).first()
                if db_item:
                    db_item.quantity = quantity
                    db.session.commit()
            else:
                self.remove_item(product_id)
            return True
        return False
    
    def remove_item(self, product_id):
        self.items = [item for item in self.items if item.product_id != product_id]
        BKL_CartItem.query.filter_by(
            session_id=self.session_id,
            product_id=product_id
        ).delete()
        db.session.commit()
    
    def clear(self):
        self.items = []
        BKL_CartItem.query.filter_by(session_id=self.session_id).delete()
        db.session.commit()
    
    @property
    def total(self):
        return sum(float(item.unit_price) * item.quantity for item in self.items)
    
    def save_to_db(self):
        try:
            existing_items = BKL_CartItem.query.filter_by(session_id=self.session_id).all()
            existing_dict = {item.product_id: item for item in existing_items}
            
            for item in self.items:
                if item.product_id in existing_dict:
                    db_item = existing_dict[item.product_id]
                    db_item.quantity = item.quantity
                    db_item.unit_price = item.unit_price
                    db_item.product_name = item.product_name
                else:
                    new_item = BKL_CartItem(
                        session_id=item.session_id,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        unit_price=item.unit_price,
                        quantity=item.quantity
                    )
                    db.session.add(new_item)
            
            current_product_ids = {item.product_id for item in self.items}
            for db_item in existing_items:
                if db_item.product_id not in current_product_ids:
                    db.session.delete(db_item)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def load_from_db(self):
        self.items = BKL_CartItem.query.filter_by(session_id=self.session_id).all()
    
    def __len__(self):
        return sum(item.quantity for item in self.items)


class BKL_Coupon(db.Model):
    __tablename__ = 'bkl_coupon'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    is_percentage = db.Column(db.Boolean, default=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    def is_valid(self):
        now = datetime.utcnow()
        return self.active and self.valid_from <= now <= self.valid_to


class BKL_Order(db.Model):
    __tablename__ = 'bkl_order'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('bkl_user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    payment_status = db.Column(db.String(50), default='Pending')
    stripe_session_id = db.Column(db.String(200), nullable=True)
    delivery_address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('BKL_OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('BKL_Feedback', backref='order', lazy=True)


class BKL_OrderItem(db.Model):
    __tablename__ = 'bkl_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('bkl_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('bkl_product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)


class BKL_Favorite(db.Model):
    __tablename__ = 'bkl_favorite'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('bkl_user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('bkl_product.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class BKL_Feedback(db.Model):
    __tablename__ = 'bkl_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('bkl_user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('bkl_order.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default='')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class BKL_Payment(db.Model):
    __tablename__ = 'bkl_payment'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('bkl_order.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Succeeded')