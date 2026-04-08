"""
用户路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import User, Address, PointsLog
from app.utils.helpers import (
    success_response, error_response, token_required,
    paginate
)

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@token_required
@swag_from({
    'tags': ['用户'],
    'summary': '获取当前用户信息',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': '用户信息'}
    }
})
def get_profile():
    """获取当前用户信息"""
    user = db.session.get(User, g.current_user_id)
    
    if not user:
        return error_response('用户不存在', 404)
    
    return success_response(user.to_dict())


@user_bp.route('/profile', methods=['PUT'])
@token_required
@swag_from({
    'tags': ['用户'],
    'summary': '更新用户信息',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'avatar': {'type': 'string'},
                'gender': {'type': 'integer'},
                'birthday': {'type': 'string'}
            }
        }
    }],
    'responses': {
        200: {'description': '更新成功'}
    }
})
def update_profile():
    """更新用户信息"""
    user = db.session.get(User, g.current_user_id)
    
    if not user:
        return error_response('用户不存在', 404)
    
    data = request.get_json()
    
    # 更新字段
    if 'username' in data:
        username = data['username'].strip()
        if username and username != user.username:
            if User.query.filter(User.username == username, User.user_id != user.user_id).first():
                return error_response('用户名已存在')
            user.username = username
    
    for field in ['avatar', 'gender', 'birthday']:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return success_response(user.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')


# ============ 地址管理 ============

@user_bp.route('/addresses', methods=['GET'])
@token_required
def get_addresses():
    """获取用户地址列表"""
    addresses = Address.query.filter_by(user_id=g.current_user_id).order_by(
        Address.is_default.desc(), Address.create_time.desc()
    ).all()
    
    return success_response([addr.to_dict() for addr in addresses])


@user_bp.route('/addresses', methods=['POST'])
@token_required
def add_address():
    """添加收货地址"""
    data = request.get_json()
    
    required = ['recipient_name', 'recipient_phone', 'province', 'city', 'detail_address']
    for field in required:
        if not data.get(field):
            return error_response(f'{field} 不能为空')
    
    # 检查地址数量限制
    count = Address.query.filter_by(user_id=g.current_user_id).count()
    if count >= 20:
        return error_response('最多只能添加20个地址')
    
    address = Address(
        user_id=g.current_user_id,
        recipient_name=data['recipient_name'],
        recipient_phone=data['recipient_phone'],
        province=data['province'],
        city=data['city'],
        district=data.get('district'),
        detail_address=data['detail_address'],
        postal_code=data.get('postal_code'),
        is_default=data.get('is_default', 0)
    )
    
    try:
        # 如果设为默认，取消其他默认地址
        if address.is_default:
            Address.query.filter_by(user_id=g.current_user_id, is_default=1).update({'is_default': 0})
        
        db.session.add(address)
        db.session.commit()
        return success_response(address.to_dict(), '添加成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加失败: {str(e)}')


@user_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@token_required
def update_address(address_id):
    """更新地址"""
    address = Address.query.filter_by(address_id=address_id, user_id=g.current_user_id).first()
    
    if not address:
        return error_response('地址不存在', 404)
    
    data = request.get_json()
    
    for field in ['recipient_name', 'recipient_phone', 'province', 'city', 
                  'district', 'detail_address', 'postal_code', 'is_default']:
        if field in data:
            setattr(address, field, data[field])
    
    try:
        if address.is_default:
            Address.query.filter(
                Address.user_id == g.current_user_id,
                Address.address_id != address_id,
                Address.is_default == 1
            ).update({'is_default': 0})
        
        db.session.commit()
        return success_response(address.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')


@user_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@token_required
def delete_address(address_id):
    """删除地址"""
    address = Address.query.filter_by(address_id=address_id, user_id=g.current_user_id).first()
    
    if not address:
        return error_response('地址不存在', 404)
    
    try:
        db.session.delete(address)
        db.session.commit()
        return success_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}')


# ============ 积分记录 ============

@user_bp.route('/points', methods=['GET'])
@token_required
def get_points_logs():
    """获取积分记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = PointsLog.query.filter_by(user_id=g.current_user_id).order_by(
        PointsLog.create_time.desc()
    )
    
    result = paginate(query, page, per_page)
    return success_response(result)
