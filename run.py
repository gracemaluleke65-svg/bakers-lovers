from app import create_app, db
from app.models import User, Product, Order, OrderItem, CartItem, Coupon, Favorite, Feedback, Payment
from flask_migrate import Migrate
import os

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Order': Order,
        'OrderItem': OrderItem,
        'CartItem': CartItem,
        'Coupon': Coupon,
        'Favorite': Favorite,
        'Feedback': Feedback,
        'Payment': Payment
    }


if __name__ == '__main__':
    # For local development only
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)