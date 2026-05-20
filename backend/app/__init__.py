"""
Flask application factory.
"""
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DBAPIError, OperationalError


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Create and configure a Flask application."""
    app = Flask(__name__)

    from app.config import config

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    Swagger(app, template={
        'swagger': '2.0',
        'info': {
            'title': 'Ecommerce Platform API',
            'description': 'Backend API for the ecommerce platform.',
            'version': '1.0.0',
        },
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT token in the format: Bearer <token>',
            }
        }
    })

    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.product import product_bp
    from app.routes.category import category_bp
    from app.routes.cart import cart_bp
    from app.routes.order import order_bp
    from app.routes.coupon import coupon_bp
    from app.routes.review import review_bp
    from app.routes.admin import admin_bp
    from app.routes.seckill import seckill_bp
    from app.routes.notification import notif_bp
    from app.routes.spec import spec_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(coupon_bp, url_prefix='/api/coupons')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(spec_bp, url_prefix='/api')
    app.register_blueprint(seckill_bp, url_prefix='/api')
    app.register_blueprint(notif_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return {
            'name': 'Ecommerce Platform API',
            'version': '1.0.0',
            'docs': '/apidocs',
            'health': '/health',
            'database_health': '/health/db',
        }


    from flask import send_from_directory
    import os
    @app.route('/static/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
        return send_from_directory(upload_dir, filename)
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Service is running'}

    @app.route('/health/db')
    def health_db():
        try:
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'ok', 'message': 'Database is reachable'}
        except OperationalError:
            return {
                'status': 'error',
                'message': 'Database is unreachable. Check remote database host, port, VPN, and firewall rules.',
            }, 503
        except DBAPIError:
            return {
                'status': 'error',
                'message': 'Database query failed. Check database availability and credentials.',
            }, 503

    @app.errorhandler(400)
    def bad_request(error):
        return {'code': 400, 'message': str(error), 'data': None}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'code': 401, 'message': 'Unauthorized', 'data': None}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'code': 403, 'message': 'Forbidden', 'data': None}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': 'Resource not found', 'data': None}, 404

    @app.errorhandler(OperationalError)
    def database_unreachable(error):
        return {
            'code': 503,
            'message': 'Database is unreachable. Check remote database host, port, VPN, and firewall rules.',
            'data': None,
        }, 503

    @app.errorhandler(DBAPIError)
    def database_error(error):
        return {
            'code': 503,
            'message': 'Database request failed. Check database availability and credentials.',
            'data': None,
        }, 503

    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': 'Internal server error', 'data': None}, 500

    return app
