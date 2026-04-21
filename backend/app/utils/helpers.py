"""
工具函数模块
"""
from datetime import datetime, timedelta
import jwt
import bcrypt
from flask import current_app, g
from functools import wraps
from flask import request, jsonify


def hash_password(password: str) -> str:
    """
    使用 bcrypt 加密密码
    
    Args:
        password: 明文密码
    
    Returns:
        加密后的密码字符串
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        password: 明文密码
        hashed_password: 加密后的密码
    
    Returns:
        是否匹配
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_token(user_id: int, expires_hours: int = None) -> str:
    """
    生成 JWT Token
    
    Args:
        user_id: 用户ID
        expires_hours: 过期时间（小时）
    
    Returns:
        JWT Token 字符串
    """
    if expires_hours is None:
        expires_hours = current_app.config.get('JWT_EXPIRATION_HOURS', 24)
    
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow()
    }
    
    secret = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key')
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def decode_token(token: str) -> dict:
    """
    解码 JWT Token
    
    Args:
        token: JWT Token 字符串
    
    Returns:
        解码后的 payload，失败返回 None
    """
    try:
        secret = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token 已过期
    except jwt.InvalidTokenError:
        return None  # 无效 Token


def token_required(f):
    """
    JWT 认证装饰器
    
    用法:
        @token_required
        def protected_route():
            user_id = g.current_user_id
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从 Header 获取 Token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({
                'code': 401,
                'message': '缺少认证 Token',
                'data': None
            }), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'code': 401,
                'message': 'Token 无效或已过期',
                'data': None
            }), 401
        
        # 保存用户ID到全局变量
        g.current_user_id = payload.get('user_id')
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        from app.models.models import User
        from app import db
        user = db.session.get(User, g.current_user_id)
        if not user or not user.is_admin:
            return jsonify({
                'code': 403,
                'message': '需要管理员权限',
                'data': None
            }), 403
        return f(*args, **kwargs)
    return decorated


def success_response(data=None, message='操作成功', code=200):
    """
    成功响应
    
    Args:
        data: 返回的数据
        message: 消息
        code: 状态码
    
    Returns:
        Flask response
    """
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code


def error_response(message='操作失败', code=400, data=None):
    """
    错误响应
    
    Args:
        message: 错误消息
        code: 错误码
        data: 额外数据
    
    Returns:
        Flask response
    """
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code


def paginate(query, page=1, per_page=20):
    """
    分页查询
    
    Args:
        query: SQLAlchemy query 对象
        page: 页码
        per_page: 每页数量
    
    Returns:
        dict: 分页结果
    """
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def generate_order_id():
    """
    生成订单号
    格式: 时间戳(13位) + 随机数(6位)
    """
    import time
    import random
    
    timestamp = int(time.time() * 1000)
    random_num = random.randint(100000, 999999)
    return int(f"{timestamp}{random_num}")
