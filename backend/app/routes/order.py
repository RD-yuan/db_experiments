"""
订单路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import Order, OrderItem, ShoppingCart, Address, User, PointsLog
from app.utils.helpers import (
    success_response, error_response, token_required,
    paginate, generate_order_id
)
import json
from datetime import datetime

order_bp = Blueprint('order', __name__)


@order_bp.route('', methods=['GET'])
@token_required
@swag_from({
    'tags': ['订单'],
    'summary': '获取订单列表',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10},
        {'name': 'status', 'in': 'query', 'type': 'integer', 'description': '订单状态筛选'}
    ],
    'responses': {
        200: {'description': '订单列表'}
    }
})
def get_orders():
    """获取订单列表"""
    user_id = g.current_user_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)

    query = Order.query.filter_by(user_id=user_id)

    if status is not None:
        query = query.filter_by(status=status)

    query = query.order_by(Order.create_time.desc())

    result = paginate(query, page, per_page)

    # 为每个订单添加商品明细
    # 注意：此时 result['items'] 中的 order_id 已经是字符串
    for order_data in result['items']:
        order = db.session.get(Order, int(order_data['order_id']))
        order_data['items'] = [item.to_dict() for item in order.items]

    return success_response(result)


@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """获取订单详情"""
    order = Order.query.filter_by(order_id=order_id, user_id=g.current_user_id).first()

    if not order:
        return error_response('订单不存在', 404)

    data = order.to_dict()
    data['items'] = [item.to_dict() for item in order.items]

    return success_response(data)


@order_bp.route('', methods=['POST'])
@token_required
@swag_from({
    'tags': ['订单'],
    'summary': '创建订单',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'address_id': {'type': 'integer'},
                'cart_ids': {'type': 'array', 'items': {'type': 'integer'}},
                'coupon_id': {'type': 'integer'},
                'points_used': {'type': 'integer'},
                'buyer_note': {'type': 'string'}
            },
            'required': ['address_id']
        }
    }],
    'responses': {
        200: {'description': '创建成功'},
        400: {'description': '参数错误'}
    }
})
def create_order():
    """创建订单"""
    user_id = g.current_user_id
    data = request.get_json()

    address_id = data.get('address_id')
    cart_ids = data.get('cart_ids', [])
    points_used = data.get('points_used', 0)
    buyer_note = data.get('buyer_note', '')

    # 验证地址
    address = Address.query.filter_by(address_id=address_id, user_id=user_id).first()
    if not address:
        return error_response('地址不存在')

    # 获取购物车商品
    if cart_ids:
        cart_items = ShoppingCart.query.filter(
            ShoppingCart.cart_id.in_(cart_ids),
            ShoppingCart.user_id == user_id
        ).all()
    else:
        cart_items = ShoppingCart.query.filter_by(user_id=user_id, selected=1).all()

    if not cart_items:
        return error_response('购物车为空')

    # 计算金额
    total_amount = 0
    order_items = []

    for item in cart_items:
        if not item.product or item.product.status != 1:
            return error_response(f'商品 {item.product.name if item.product else ""} 已下架')

        if item.product.available_stock < item.quantity:
            return error_response(f'商品 {item.product.name} 库存不足')

        price = float(item.product.price)
        subtotal = price * item.quantity
        total_amount += subtotal

        order_items.append({
            'product': item.product,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'product_image': item.product.main_image,
            'price': price,
            'quantity': item.quantity,
            'subtotal': subtotal
        })

    # 优惠券折扣（简化处理）
    discount_amount = 0

    # 积分抵扣
    user = db.session.get(User, user_id)
    points_discount = 0
    if points_used > 0:
        if points_used > user.points:
            return error_response('积分不足')
        points_discount = min(points_used * 0.01, total_amount - discount_amount)  # 100积分=1元
        points_used = int(points_discount * 100)

    # 计算实付金额
    freight_amount = 0 if total_amount >= 99 else 10  # 满99包邮
    payment_amount = total_amount + freight_amount - discount_amount - points_discount

    # 生成订单号
    order_id = generate_order_id()

    # 创建订单
    order = Order(
        order_id=order_id,
        user_id=user_id,
        total_amount=total_amount,
        freight_amount=freight_amount,
        discount_amount=discount_amount,
        points_used=points_used,
        points_discount=points_discount,
        payment_amount=payment_amount,
        address_snapshot=json.dumps(address.to_dict(), ensure_ascii=False),
        buyer_note=buyer_note
    )

    try:
        db.session.add(order)
        db.session.flush()  # 获取 order_id

        # 创建订单明细
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data['product_id'],
                product_name=item_data['product_name'],
                product_image=item_data['product_image'],
                price=item_data['price'],
                quantity=item_data['quantity'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)

            # 锁定库存
            if item_data['product'].locked_stock is None:
                item_data['product'].locked_stock = 0
            item_data['product'].locked_stock += item_data['quantity']

        # 删除购物车
        for item in cart_items:
            db.session.delete(item)

        # 扣减积分
        if points_used > 0:
            user.points -= points_used
            points_log = PointsLog(
                user_id=user_id,
                type=2,  # 支出
                amount=points_used,
                balance_after=user.points,
                source='ORDER',
                source_id=str(order_id),
                description=f'订单 {order_id} 使用积分'
            )
            db.session.add(points_log)

        db.session.commit()

        return success_response({
            'order_id': str(order_id),  # 返回字符串，确保前端精度
            'payment_amount': float(payment_amount)
        }, '订单创建成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'创建失败: {str(e)}')


@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(order_id):
    """取消订单"""
    order = Order.query.filter_by(order_id=order_id, user_id=g.current_user_id).first()

    if not order:
        return error_response('订单不存在', 404)

    if order.status != 0:
        return error_response('只能取消待支付订单')

    try:
        # 释放锁定库存
        for item in order.items:
            product = item.product
            if product:
                product.locked_stock -= item.quantity

        order.status = 4  # 已取消

        # 退还积分
        if order.points_used > 0:
            user = order.user
            user.points += order.points_used
            points_log = PointsLog(
                user_id=user.user_id,
                type=1,
                amount=order.points_used,
                balance_after=user.points,
                source='REFUND',
                source_id=str(order_id),
                description=f'订单 {order_id} 取消退还积分'
            )
            db.session.add(points_log)

        db.session.commit()
        return success_response(message='订单已取消')

    except Exception as e:
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}')


@order_bp.route('/<int:order_id>/pay', methods=['POST'])
@token_required
def pay_order(order_id):
    """支付订单（包含余额检查与扣款）"""
    order = Order.query.filter_by(order_id=order_id, user_id=g.current_user_id).first()

    if not order:
        return error_response('订单不存在', 404)

    if order.status != 0:
        return error_response('订单状态不正确')

    # 获取用户信息
    user = order.user

    # 核心修复：余额校验
    # 假设 payment_method = 3 是“余额支付”
    
    if user.balance < order.payment_amount:
        return error_response('账户余额不足，请先充值')

    try:
        # 1. 执行扣款 (仅当使用余额支付时)
        
        user.balance -= order.payment_amount

        # 2. 扣减库存 (原逻辑)
        for item in order.items:
            product = item.product
            if product:
                if product.stock < item.quantity:
                    raise Exception(f'商品 {product.name} 库存不足')
                product.stock -= item.quantity
                product.locked_stock -= item.quantity
                product.sold_count += item.quantity

        # 3. 更新订单状态
        order.status = 1  # 已支付
        order.payment_time = datetime.utcnow()
        order.transaction_id = f"PAY_{order_id}"

        # 4. 赠送积分 (原逻辑)
        earned_points = int(float(order.payment_amount))
        user.points += earned_points

        points_log = PointsLog(
            user_id=user.user_id,
            type=1,
            amount=earned_points,
            balance_after=user.points,
            source='ORDER',
            source_id=str(order_id),
            description=f'订单 {order_id} 购物赠送'
        )
        db.session.add(points_log)

        db.session.commit()
        return success_response(message='支付成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'支付失败: {str(e)}')


@order_bp.route('/<int:order_id>/receive', methods=['POST'])
@token_required
def receive_order(order_id):
    """确认收货"""
    order = Order.query.filter_by(order_id=order_id, user_id=g.current_user_id).first()

    if not order:
        return error_response('订单不存在', 404)

    if order.status != 2:
        return error_response('只能确认已发货的订单')

    try:
        from datetime import datetime
        order.status = 3  # 已完成
        order.receive_time = datetime.utcnow()

        db.session.commit()
        return success_response(message='已确认收货')

    except Exception as e:
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}')
