"""
管理员路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import User, Product, Order, OperationLog
from app.utils.helpers import (
    success_response, error_response, admin_required, paginate
)
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


# ============ 用户管理 ============

@admin_bp.route('/users', methods=['GET'])
@admin_required
@swag_from({
    'tags': ['管理员'],
    'summary': '获取用户列表',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 20},
        {'name': 'keyword', 'in': 'query', 'type': 'string'}
    ],
    'responses': {
        200: {'description': '用户列表'}
    }
})
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '').strip()
    
    query = User.query
    
    if keyword:
        query = query.filter(
            db.or_(
                User.username.like(f'%{keyword}%'),
                User.phone.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%')
            )
        )
    
    query = query.order_by(User.create_time.desc())
    result = paginate(query, page, per_page)
    
    return success_response(result)


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """启用/禁用用户"""
    data = request.get_json()
    status = data.get('status')
    
    if status not in [0, 1]:
        return error_response('状态值无效')
    
    user = db.session.get(User, user_id)
    if not user:
        return error_response('用户不存在', 404)
    
    if user.user_id == 1:
        return error_response('不能禁用管理员')
    
    try:
        user.status = status
        db.session.commit()
        return success_response(message='操作成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}')


@admin_bp.route('/users/<int:user_id>/vip', methods=['PUT'])
@admin_required
def set_user_vip(user_id):
    """设置用户VIP"""
    data = request.get_json()
    
    user = db.session.get(User, user_id)
    if not user:
        return error_response('用户不存在', 404)
    
    user.is_vip = data.get('is_vip', 0)
    user.vip_level = data.get('vip_level', 0)
    
    if data.get('vip_months'):
        user.vip_expire_time = datetime.utcnow() + timedelta(days=data['vip_months'] * 30)
    
    try:
        db.session.commit()
        return success_response(user.to_dict(), '设置成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'设置失败: {str(e)}')


# ============ 订单管理 ============

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """获取所有订单"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', type=int)
    
    query = Order.query
    
    if status is not None:
        query = query.filter_by(status=status)
    
    query = query.order_by(Order.create_time.desc())
    result = paginate(query, page, per_page)
    
    return success_response(result)


@admin_bp.route('/orders/<int:order_id>/ship', methods=['POST'])
@admin_required
def ship_order(order_id):
    """发货"""
    order = db.session.get(Order, order_id)
    
    if not order:
        return error_response('订单不存在', 404)
    
    if order.status != 1:
        return error_response('只能发货已支付订单')
    
    data = request.get_json()
    shipping_company = data.get('shipping_company')
    shipping_number = data.get('shipping_number')
    
    if not shipping_company or not shipping_number:
        return error_response('物流信息不完整')
    
    try:
        order.status = 2
        order.shipping_company = shipping_company
        order.shipping_number = shipping_number
        order.shipping_time = datetime.utcnow()
        
        db.session.commit()
        return success_response(message='发货成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'发货失败: {str(e)}')


# ============ 数据统计 ============

@admin_bp.route('/stats/overview', methods=['GET'])
@admin_required
def get_overview():
    """数据概览"""
    # 今日日期
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    # 总用户数
    total_users = User.query.count()
    
    # 今日新增用户
    new_users_today = User.query.filter(User.create_time >= today_start).count()
    
    # 总订单数
    total_orders = Order.query.count()
    
    # 今日订单数
    orders_today = Order.query.filter(Order.create_time >= today_start).count()
    
    # 今日销售额
    today_sales = db.session.query(
        func.sum(Order.payment_amount)
    ).filter(
        Order.create_time >= today_start,
        Order.status.in_([1, 2, 3])
    ).scalar() or 0
    
    # 总销售额
    total_sales = db.session.query(
        func.sum(Order.payment_amount)
    ).filter(Order.status.in_([1, 2, 3])).scalar() or 0
    
    # 商品数量
    total_products = Product.query.count()
    
    return success_response({
        'total_users': total_users,
        'new_users_today': new_users_today,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'total_sales': float(total_sales),
        'today_sales': float(today_sales),
        'total_products': total_products
    })


@admin_bp.route('/stats/hot-products', methods=['GET'])
@admin_required
def get_hot_products():
    """热销商品Top10"""
    limit = request.args.get('limit', 10, type=int)
    
    products = Product.query.filter_by(status=1).order_by(
        Product.sold_count.desc()
    ).limit(limit).all()
    
    return success_response([p.to_dict() for p in products])


@admin_bp.route('/stats/sales-trend', methods=['GET'])
@admin_required
def get_sales_trend():
    """销售趋势（最近7天）"""
    days = request.args.get('days', 7, type=int)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按日期统计
    result = db.session.query(
        func.date(Order.create_time).label('date'),
        func.count(Order.order_id).label('order_count'),
        func.sum(Order.payment_amount).label('sales_amount')
    ).filter(
        Order.create_time >= start_date,
        Order.status.in_([1, 2, 3])
    ).group_by(
        func.date(Order.create_time)
    ).all()
    
    trend = [{
        'date': str(r.date),
        'order_count': r.order_count,
        'sales_amount': float(r.sales_amount or 0)
    } for r in result]
    
    return success_response(trend)
