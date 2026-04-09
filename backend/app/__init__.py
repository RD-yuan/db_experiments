"""
Flask 应用工厂
"""
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """
    创建 Flask 应用实例
    
    Args:
        config_name: 配置名称 (development/production/testing)
    
    Returns:
        Flask app 实例
    """
    app = Flask(__name__)
    
    # 加载配置
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    Swagger(app, template={
        'swagger': '2.0',
        'info': {
            'title': '电子商务平台 API',
            'description': '基于 Flask 的电子商务平台后端 API',
            'version': '1.0.0'
        },
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Token, 格式: Bearer <token>'
            }
        }
    })
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.product import product_bp
    from app.routes.category import category_bp
    from app.routes.cart import cart_bp
    from app.routes.order import order_bp
    from app.routes.coupon import coupon_bp
    from app.routes.review import review_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(coupon_bp, url_prefix='/api/coupons')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # 根路由
    @app.route('/')
    def index():
        return {
            'name': '电子商务平台 API',
            'version': '1.0.0',
            'docs': '/apidocs',
            'health': '/health'
        }

    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Service is running'}
    
    # 全局错误处理
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
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': 'Internal server error', 'data': None}, 500
    
    return app
