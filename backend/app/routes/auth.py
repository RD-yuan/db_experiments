"""
认证路由 - 注册、登录
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app import db
from app.models.models import User
from app.utils.helpers import (
    hash_password, verify_password, generate_token,
    success_response, error_response
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['认证'],
    'summary': '用户注册',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'example': 'testuser'},
                'password': {'type': 'string', 'example': '123456'},
                'phone': {'type': 'string', 'example': '13800138000'},
                'email': {'type': 'string', 'example': 'test@example.com'}
            },
            'required': ['username', 'password']
        }
    }],
    'responses': {
        200: {'description': '注册成功'},
        400: {'description': '参数错误'}
    }
})
def register():
    """用户注册"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    phone = data.get('phone', '').strip() or None
    email = data.get('email', '').strip() or None
    
    # 参数验证
    if not username or not password:
        return error_response('用户名和密码不能为空')
    
    if len(username) < 2 or len(username) > 50:
        return error_response('用户名长度需在2-50个字符之间')
    
    if len(password) < 6:
        return error_response('密码长度至少6个字符')
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return error_response('用户名已存在')
    
    # 检查手机号是否已存在
    if phone and User.query.filter_by(phone=phone).first():
        return error_response('手机号已被注册')
    
    # 检查邮箱是否已存在
    if email and User.query.filter_by(email=email).first():
        return error_response('邮箱已被注册')
    
    # 创建用户
    user = User(
        username=username,
        password=hash_password(password),
        phone=phone,
        email=email
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # 生成 Token
        token = generate_token(user.user_id)
        
        return success_response({
            'user': user.to_dict(),
            'token': token
        }, '注册成功')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'注册失败: {str(e)}')


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['认证'],
    'summary': '用户登录',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'example': 'testuser'},
                'password': {'type': 'string', 'example': '123456'}
            },
            'required': ['username', 'password']
        }
    }],
    'responses': {
        200: {'description': '登录成功'},
        401: {'description': '认证失败'}
    }
})
def login():
    """用户登录"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return error_response('用户名和密码不能为空', 401)
    
    # 支持用户名/手机号/邮箱登录
    user = User.query.filter(
        (User.username == username) | 
        (User.phone == username) | 
        (User.email == username)
    ).first()
    
    if not user:
        return error_response('用户不存在', 401)
    
    if user.status == 0:
        return error_response('账号已被禁用', 401)
    
    if not verify_password(password, user.password):
        return error_response('密码错误', 401)
    
    # 更新登录信息
    from datetime import datetime
    user.last_login_time = datetime.utcnow()
    user.last_login_ip = request.remote_addr
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # 生成 Token
    token = generate_token(user.user_id)
    
    return success_response({
        'user': user.to_dict(),
        'token': token
    }, '登录成功')


@auth_bp.route('/logout', methods=['POST'])
@swag_from({
    'tags': ['认证'],
    'summary': '用户登出',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': '登出成功'}
    }
})
def logout():
    """用户登出（前端清除 Token 即可）"""
    return success_response(message='登出成功')
