"""
用户路由
"""
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta

from flask import Blueprint, request, g, current_app
from flasgger import swag_from
from app import db
from app.models.models import User, Address, PointsLog, Order, OrderItem, Product, Category
from app.utils.helpers import (
    success_response, error_response, token_required,
    paginate
)
from app.utils.validators import (
    is_valid_email, is_valid_phone, normalize_email, normalize_optional_text
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
                'email': {'type': 'string'},
                'phone': {'type': 'string'},
                'avatar': {'type': 'string'},
                'gender': {'type': 'integer'},
                'birthday': {'type': 'string'}
            }
        }
    }],
    'responses': {200: {'description': '更新成功'}}
})
def update_profile():
    """更新用户信息"""
    user = db.session.get(User, g.current_user_id)
    if not user:
        return error_response('用户不存在', 404)

    data = request.get_json() or {}

    # 更新用户名
    if 'username' in data:
        username = data['username'].strip()
        if username and username != user.username:
            if User.query.filter(User.username == username, User.user_id != user.user_id).first():
                return error_response('用户名已存在')
            user.username = username

    # 更新邮箱
    if 'email' in data:
        email = normalize_email(data.get('email'))
        if email and not is_valid_email(email):
            return error_response('邮箱格式不正确')
        if email and email != user.email:
            if User.query.filter(User.email == email, User.user_id != user.user_id).first():
                return error_response('邮箱已被使用')
            user.email = email
        elif email is None:
            user.email = None

    # 更新手机号
    if 'phone' in data:
        phone = normalize_optional_text(data.get('phone'))
        if phone and not is_valid_phone(phone):
            return error_response('手机号格式不正确')
        if phone and phone != user.phone:
            if User.query.filter(User.phone == phone, User.user_id != user.user_id).first():
                return error_response('手机号已被使用')
            user.phone = phone
        elif phone is None:
            user.phone = None

    # 其他字段
    if 'avatar' in data:
        user.avatar = data['avatar']
    if 'gender' in data:
        try:
            user.gender = int(data['gender'])
        except (TypeError, ValueError):
            return error_response('性别参数格式错误')
    if 'birthday' in data:
        birthday = data['birthday']
        if birthday:
            try:
                user.birthday = datetime.strptime(birthday[:10], '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return error_response('生日格式错误')
        else:
            user.birthday = None

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


# user.py

@user_bp.route('/recharge', methods=['POST'])
@token_required
def recharge():
    """账户充值 (模拟)"""
    data = request.get_json() or {}
    amount = data.get('amount')

    try:
        recharge_amount = Decimal(str(amount)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return error_response('请输入正确的充值金额')

    if recharge_amount <= 0:
        return error_response('请输入正确的充值金额')

    user = db.session.get(User, g.current_user_id)
    if not user:
        return error_response('用户不存在', 404)

    try:
        user.balance = (user.balance or Decimal('0.00')) + recharge_amount
        db.session.commit()
        return success_response({'new_balance': float(user.balance)}, '充值成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'充值失败: {str(e)}')

@user_bp.route('/addresses', methods=['POST'])
@token_required
def add_address():
    """添加收货地址"""
    data = request.get_json() or {}
    
    required = ['recipient_name', 'recipient_phone', 'province', 'city', 'detail_address']
    for field in required:
        if not data.get(field):
            return error_response(f'{field} 不能为空')

    recipient_phone = normalize_optional_text(data.get('recipient_phone'))
    if not is_valid_phone(recipient_phone):
        return error_response('收货人手机号格式不正确')
    
    # 检查地址数量限制
    count = Address.query.filter_by(user_id=g.current_user_id).count()
    if count >= 20:
        return error_response('最多只能添加20个地址')
    
    address = Address(
        user_id=g.current_user_id,
        recipient_name=data['recipient_name'],
        recipient_phone=recipient_phone,
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
    
    data = request.get_json() or {}

    if 'recipient_phone' in data:
        recipient_phone = normalize_optional_text(data.get('recipient_phone'))
        if not is_valid_phone(recipient_phone):
            return error_response('收货人手机号格式不正确')
        data['recipient_phone'] = recipient_phone
    
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


# ============ 消费统计 ============

@user_bp.route('/consumption-stats', methods=['GET'])
@token_required
def get_consumption_stats():
    """获取消费统计数据（兼容 MySQL / SQLite）"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from collections import defaultdict

    user_id = g.current_user_id
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    period = request.args.get('period', 'daily')  # daily/weekly/monthly

    # 默认查询最近30天
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')

    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

    try:
        # 总体统计
        total_stats = db.session.query(
            func.count(Order.order_id).label('total_orders'),
            func.sum(Order.payment_amount).label('total_amount')
        ).filter(
            Order.user_id == user_id,
            Order.status.in_([1, 2, 3]),
            Order.create_time >= start_datetime,
            Order.create_time < end_datetime
        ).first()

        # 查询订单原始数据（不做日期格式化，由 Python 处理分组）
        orders = db.session.query(
            Order.create_time,
            Order.payment_amount
        ).filter(
            Order.user_id == user_id,
            Order.status.in_([1, 2, 3]),
            Order.create_time >= start_datetime,
            Order.create_time < end_datetime
        ).all()

        # 按商品分类统计消费占比
        category_stats = db.session.query(
            Category.name.label('category_name'),
            func.sum(OrderItem.subtotal).label('amount')
        ).join(
            Product, Product.product_id == OrderItem.product_id
        ).join(
            Category, Category.category_id == Product.category_id
        ).join(
            Order, Order.order_id == OrderItem.order_id
        ).filter(
            Order.user_id == user_id,
            Order.status.in_([1, 2, 3]),
            Order.create_time >= start_datetime,
            Order.create_time < end_datetime
        ).group_by(Category.name).all()

        # 按周期聚合数据
        trend_map = defaultdict(lambda: {'order_count': 0, 'amount': 0.0})
        for create_time, amount in orders:
            if period == 'daily':
                key = create_time.strftime('%Y-%m-%d')
            elif period == 'weekly':
                iso_year, iso_week, _ = create_time.isocalendar()
                key = f'{iso_year}-{iso_week:02d}'
            else:  # monthly
                key = create_time.strftime('%Y-%m')
            trend_map[key]['order_count'] += 1
            trend_map[key]['amount'] += float(amount or 0)

        # 转换为列表并按日期排序
        trend_data = [
            {
                'date': key,
                'order_count': val['order_count'],
                'amount': round(val['amount'], 2)
            }
            for key, val in sorted(trend_map.items())
        ]

        return success_response({
            'total_stats': {
                'total_orders': total_stats.total_orders or 0,
                'total_amount': float(total_stats.total_amount or 0)
            },
            'trend': trend_data,
            'category_distribution': [{
                'name': c.category_name,
                'value': float(c.amount or 0)
            } for c in category_stats]
        })
    except Exception as e:
        # 如果仍失败，记录详细错误并返回友好提示
        current_app.logger.error(f"消费统计查询失败: {str(e)}", exc_info=True)
        return error_response(f'统计查询失败，请稍后重试', 500)

# ============ VIP 购买 ============

@user_bp.route('/vip/packages', methods=['GET'])
def get_vip_packages():
    """获取VIP套餐列表"""
    packages = current_app.config.get('VIP_PACKAGES', [])
    return success_response(packages)


@user_bp.route('/vip/purchase', methods=['POST'])
@token_required
def purchase_vip():
    """购买VIP（余额支付）"""
    from datetime import timedelta

    user = db.session.get(User, g.current_user_id)
    if not user:
        return error_response('用户不存在', 404)

    data = request.get_json() or {}
    package_index = data.get('package_index')
    if package_index is None:
        return error_response('请选择套餐')

    packages = current_app.config.get('VIP_PACKAGES', [])
    try:
        pkg = packages[int(package_index)]
    except (IndexError, ValueError):
        return error_response('套餐不存在')

    price = Decimal(str(pkg['price']))
    if user.balance < price:
        return error_response('余额不足，请先充值')

    months = pkg['months']
    level = pkg['level']
    now = datetime.utcnow()
    active_vip = bool(user.is_vip and user.vip_expire_time and user.vip_expire_time > now)
    current_level = user.vip_level or 0
    if active_vip and level < current_level:
        return error_response('已有更高等级VIP，请选择同级或更高等级套餐')

    try:
        # 扣款
        user.balance -= price

        # 更新VIP信息
        if active_vip:
            user.vip_expire_time = user.vip_expire_time + timedelta(days=months * 30)
            user.vip_level = level
            user.is_vip = 1
        else:
            # 新开通或已过期
            user.is_vip = 1
            user.vip_level = level
            user.vip_expire_time = now + timedelta(days=months * 30)

        # 可选：赠送积分（示例：每消费1元送10积分）
        # earned_points = int(price * 10)
        # user.points += earned_points
        # points_log = PointsLog(...)
        # db.session.add(points_log)

        db.session.commit()
        return success_response(user.to_dict(), 'VIP开通成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'购买失败: {str(e)}')
