from decimal import Decimal
import json
from app.routes.seckill import _restore_seckill_stock
from datetime import datetime

from flask import Blueprint, request, g, current_app
from flasgger import swag_from
from app import db
from app.models.models import Order, OrderItem, ShoppingCart, Address, User, PointsLog, Product, ProductSku, UserCoupon, Coupon, Refund
from app.utils.coupon_grant import grant_order_amount_coupon
from app.utils.helpers import (
    success_response, error_response, token_required,
    paginate, generate_order_id, log_operation
)

order_bp = Blueprint('order', __name__)


def _get_effective_product_price(product, user):
    normal_price = product.price or Decimal('0.00')
    vip_price = product.vip_price

    # 基础价格：会员且会员价有效则取会员价，否则原价
    if user and user.has_active_vip() and vip_price and vip_price > 0 and vip_price < normal_price:
        base_price = vip_price
    else:
        base_price = normal_price

    # 应用等级折扣（仅VIP用户享受）
    if user and user.has_active_vip():
        benefits = current_app.config.get('VIP_BENEFITS', {}).get(user.vip_level, {})
        discount = benefits.get('discount', 1.0)
        return base_price * Decimal(str(discount))

    return base_price

def _calculate_coupon_discount(coupon, total_amount):
    """计算优惠券抵扣金额，返回 (discount_amount, error_msg)"""
    total = Decimal(str(total_amount))

    def clamp_discount(discount):
        return max(Decimal('0.00'), min(Decimal(str(discount)), total))

    if coupon.type == 1:  # 满减券
        if total < coupon.min_order_amount:
            return Decimal('0.00'), f'订单金额不满足满{coupon.min_order_amount}减{coupon.value}'
        return clamp_discount(coupon.value), None
    elif coupon.type == 2:  # 折扣券
        if total < coupon.min_order_amount:
            return Decimal('0.00'), f'订单金额不满足使用门槛{coupon.min_order_amount}'
        discount = total * (1 - Decimal(str(coupon.value)))
        if coupon.max_discount:
            max_discount = Decimal(str(coupon.max_discount))
            if discount > max_discount:
                discount = max_discount
        return clamp_discount(discount), None
    elif coupon.type == 3:  # 代金券
        if total < coupon.min_order_amount:
            return Decimal('0.00'), f'订单金额不满足使用门槛{coupon.min_order_amount}'
        return clamp_discount(coupon.value), None
    return Decimal('0.00'), '优惠券类型无效'

def cancel_expired_orders():
    """取消超过10分钟未支付的订单"""
    from datetime import timedelta
    from app.models.models import ProductSku, PointsLog, UserCoupon

    deadline = datetime.now() - timedelta(minutes=10)
    expired = Order.query.filter(
        Order.status == 0,
        Order.create_time < deadline
    ).all()

    for order in expired:
        try:
            # 释放锁定的 SKU 库存
            for item in order.items:
                if item.sku_id:
                    sku = db.session.get(ProductSku, item.sku_id)
                    if sku:
                        sku.locked_stock = max(0, (sku.locked_stock or 0) - item.quantity)
                if item.product:
                    item.product.locked_stock = max(0, (item.product.locked_stock or 0) - item.quantity)
                    # 同步 product locked_stock
                    if item.product.has_sku:
                        all_skus = ProductSku.query.filter_by(product_id=item.product.product_id).all()
                        item.product.locked_stock = sum(max(0, (s.locked_stock or 0)) for s in all_skus)

            # 退还积分
            if order.points_used > 0:
                user = order.user
                if user:
                    user.points = (user.points or 0) + order.points_used

            # 退还优惠券
            uc = UserCoupon.query.filter_by(
                user_id=order.user_id, order_id=order.order_id, status=1
            ).first()
            if uc:
                uc.status = 0
                uc.use_time = None
                uc.order_id = None

            # 恢复秒杀库存
            from app.routes.seckill import _restore_seckill_stock
            _restore_seckill_stock(order)

            order.status = 4  # 已取消
            db.session.commit()
        except Exception:
            db.session.rollback()


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
    cancel_expired_orders()
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
    for order_data in result['items']:
        order = db.session.get(Order, int(order_data['order_id']))
        order_data['items'] = [item.to_dict() for item in order.items]

    return success_response(result)


@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """获取订单详情"""
    user = db.session.get(User, g.current_user_id)
    
    if user and user.is_admin:
        order = Order.query.filter_by(order_id=order_id).first()
    else:
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
    data = request.get_json() or {}

    address_id = data.get('address_id')
    cart_ids = data.get('cart_ids', [])
    try:
        points_used = int(data.get('points_used', 0) or 0)
    except (TypeError, ValueError):
        return error_response('积分参数格式错误')
    if points_used < 0:
        return error_response('积分不能为负数')
    buyer_note = data.get('buyer_note', '')
    user = db.session.get(User, user_id)
    if not user:
        return error_response('用户不存在', 404)

    address = Address.query.filter_by(address_id=address_id, user_id=user_id).first()
    if not address:
        return error_response('地址不存在')

    if cart_ids:
        cart_items = ShoppingCart.query.filter(
            ShoppingCart.cart_id.in_(cart_ids),
            ShoppingCart.user_id == user_id
        ).all()
    else:
        cart_items = ShoppingCart.query.filter_by(user_id=user_id, selected=1).all()

    if not cart_items:
        return error_response('购物车为空')

    total_amount = Decimal('0.00')
    order_items = []

    for item in cart_items:
        product = item.product
        if not product or product.status != 1:
            return error_response(f'商品 {product.name if product else ""} 已下架')

        sku = None
        if item.sku_id:
            sku = db.session.get(ProductSku, item.sku_id)
            if not sku or sku.product_id != item.product_id:
                return error_response(f'商品 {product.name} 的SKU不存在')
            if sku.status != 1:
                return error_response(f'商品 {product.name} - {sku.spec_text} 已不可购买')
            if sku.available_stock < item.quantity:
                return error_response(f'商品 {product.name} - {sku.spec_text} 库存不足')
        elif product.has_sku:
            return error_response(f'商品 {product.name} 请选择规格')
        elif product.available_stock < item.quantity:
            return error_response(f'商品 {product.name} 库存不足')

        if sku:
            sku_base = sku.price or product.price
            if user and user.has_active_vip():
                benefits = current_app.config.get('VIP_BENEFITS', {}).get(user.vip_level, {})
                rate = benefits.get('discount', 1.0)
                sku_base = sku_base * Decimal(str(rate))
            price = sku_base
        else:
            price = _get_effective_product_price(product, user)
        subtotal = price * item.quantity
        total_amount += subtotal

        order_items.append({
            'product': product,
            'sku': sku,
            'product_id': item.product_id,
            'product_name': product.name,
            'product_image': (sku.image if sku and sku.image else product.main_image),
            'sku_id': sku.sku_id if sku else 0,
            'sku_text': sku.spec_text if sku else None,
            'price': price,
            'quantity': item.quantity,
            'subtotal': subtotal
        })
    # ========== 优惠券处理 ==========
    coupon_discount = Decimal('0.00')
    used_user_coupon = None
    user_coupon_id = data.get('coupon_id')  # 前端传递 user_coupon_id
    if user_coupon_id:
        user_coupon = UserCoupon.query.filter_by(
            user_coupon_id=user_coupon_id, user_id=user_id, status=0, order_id=None
        ).first()
        if not user_coupon:
            return error_response('优惠券不存在或已使用')
        coupon = user_coupon.coupon
        if not coupon or coupon.status != 1:
            return error_response('优惠券已失效')
        now = datetime.now()
        if coupon.start_time > now or coupon.end_time < now:
            return error_response('优惠券不在有效期内')
        if coupon.is_vip_only and not user.has_active_vip():
            return error_response('该优惠券仅限VIP使用')

        discount, err = _calculate_coupon_discount(coupon, total_amount)
        if err:
            return error_response(err)
        coupon_discount = discount
        used_user_coupon = user_coupon
    # ===================================

    discount_amount = coupon_discount
    points_discount = Decimal('0.00')
    if points_used > 0:
        if points_used > user.points:
            return error_response('积分不足')
        max_points_discount = min(
            Decimal(user.points) * Decimal('0.01'),   # 可用积分换算金额
            total_amount * Decimal('0.5')             # 订单总额的50%
        )
        points_discount = min(
            Decimal(points_used) * Decimal('0.01'),
            total_amount - discount_amount,
            max_points_discount
        )
        if Decimal(points_used) * Decimal('0.01') > max_points_discount:
            return error_response(f'积分抵扣金额不能超过 ¥{max_points_discount:.2f}')
        points_used = int(points_discount * 100)

    freight_amount = Decimal('0.00') if total_amount >= Decimal('300.00') else Decimal('12.00')
    payment_amount = max(
        Decimal('0.00'),
        total_amount + freight_amount - discount_amount - points_discount
    )
    order_id = generate_order_id()

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
        db.session.flush()

        for item_data in order_items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data['product_id'],
                product_name=item_data['product_name'],
                product_image=item_data['product_image'],
                sku_id=item_data['sku_id'],
                sku_text=item_data['sku_text'],
                price=item_data['price'],
                quantity=item_data['quantity'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)
            if item_data.get('sku'):
                if item_data['sku'].locked_stock is None:
                    item_data['sku'].locked_stock = 0
                item_data['sku'].locked_stock += item_data['quantity']
                if item_data['product'].locked_stock is None:
                    item_data['product'].locked_stock = 0
                item_data['product'].locked_stock += item_data['quantity']
            else:
                if item_data['product'].locked_stock is None:
                    item_data['product'].locked_stock = 0
                item_data['product'].locked_stock += item_data['quantity']

        for item in cart_items:
            db.session.delete(item)

        if points_used > 0:
            user.points -= points_used
            points_log = PointsLog(
                user_id=user_id,
                type=2,
                amount=points_used,
                balance_after=user.points,
                source='ORDER',
                source_id=str(order_id),
                description=f'订单 {order_id} 使用积分'
            )
            db.session.add(points_log)
        if used_user_coupon:
            used_user_coupon.order_id = order_id
        db.session.commit()
        return success_response({
            'order_id': str(order_id),
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
        restored_seckill_stock = _restore_seckill_stock(order) if order.payment_method == 5 else 0
        if order.payment_method != 5 or restored_seckill_stock == 0:
            for item in order.items:
                product = item.product
                if not product:
                    continue
                if item.sku_id:
                    sku = db.session.get(ProductSku, item.sku_id)
                    if sku:
                        sku.locked_stock = max(0, (sku.locked_stock or 0) - item.quantity)
                    product.locked_stock = max(0, (product.locked_stock or 0) - item.quantity)
                else:
                    product.locked_stock = max(0, (product.locked_stock or 0) - item.quantity)

        order.status = 4

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

        used_coupon = UserCoupon.query.filter(
            UserCoupon.user_id == order.user_id,
            UserCoupon.order_id == order.order_id,
            UserCoupon.status.in_([0, 1])
        ).first()
        if used_coupon:
            used_coupon.status = 0
            used_coupon.use_time = None
            used_coupon.order_id = None

        db.session.commit()
        log_operation(g.current_user_id, 'CANCEL_ORDER', f'取消订单 #{order_id}')
        return success_response(message='订单已取消')

    except Exception as e:
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}')


@order_bp.route('/<int:order_id>/pay', methods=['POST'])
@token_required
def pay_order(order_id):
    """支付订单（模拟）"""
    order = Order.query.filter_by(order_id=order_id, user_id=g.current_user_id).first()

    if not order:
        return error_response('订单不存在', 404)

    if order.status != 0:
        return error_response('订单状态不正确')

    user = order.user
    user_balance = user.balance or Decimal('0.00')
    if user_balance < order.payment_amount:
        return error_response('账户余额不足，请先充值')

    try:
        user.balance = user_balance - order.payment_amount

        for item in order.items:
            product = item.product
            if not product:
                continue
            # SKU 商品：更新对应 SKU 的库存
            if item.sku_id:
                sku = db.session.get(ProductSku, item.sku_id)
                if not sku:
                    raise Exception(f'商品 {product.name} 的SKU不存在')
                if (sku.stock or 0) < item.quantity:
                    raise Exception(f'商品 {product.name} - {sku.spec_text} 库存不足')
                sku.stock = (sku.stock or 0) - item.quantity
                sku.locked_stock = max(0, (sku.locked_stock or 0) - item.quantity)
                product.stock = max(0, (product.stock or 0) - item.quantity)
                product.locked_stock = max(0, (product.locked_stock or 0) - item.quantity)
            else:
                if (product.stock or 0) < item.quantity:
                    raise Exception(f'商品 {product.name} 库存不足')
                product.stock = (product.stock or 0) - item.quantity
                product.locked_stock = max(0, (product.locked_stock or 0) - item.quantity)
            product.sold_count = (product.sold_count or 0) + item.quantity

        order.status = 1
        if not order.payment_method:
            order.payment_method = 3
        order.payment_time = datetime.now()
        order.transaction_id = f"PAY_{order_id}"

        used_coupon = UserCoupon.query.filter_by(
            user_id=order.user_id,
            order_id=order.order_id,
            status=0
        ).first()
        if used_coupon:
            used_coupon.status = 1
            used_coupon.use_time = datetime.now()

        # 计算赠送积分（VIP按等级倍率加成）
        user = order.user   # 已经定义过
        if user.has_active_vip():
            benefits = current_app.config.get('VIP_BENEFITS', {}).get(user.vip_level, {})
            rate = benefits.get('points_rate', 1.0)
            earned_points = int(float(order.payment_amount) * rate)
        else:
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

        try:
            grant_order_amount_coupon(user.user_id, order.payment_amount)
        except Exception:
            pass

        db.session.commit()
        log_operation(g.current_user_id, 'PAY_ORDER', f'支付订单 #{order_id}，金额 ¥{float(order.payment_amount):.2f}')
        return success_response(message='支付成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'支付失败: {str(e)}')


@order_bp.route('/<int:order_id>/receive', methods=['POST'])
@token_required
def receive_order(order_id):
    """确认收货（仅限订单所属用户）"""
    order = Order.query.filter_by(order_id=order_id).first()

    if not order:
        return error_response('订单不存在', 404)

    # 只有订单所有者可以确认收货，管理员也不能代替
    if order.user_id != g.current_user_id:
        return error_response('无权操作此订单', 403)

    if order.status != 2:
        return error_response('只能确认已发货的订单')

    try:
        order.status = 3
        order.receive_time = datetime.now()
        db.session.commit()
        return success_response(message='已确认收货')
    except Exception as e:
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}')

@order_bp.route('/exchange', methods=['POST'])
@token_required
def create_exchange_order():
    """积分兑换下单"""
    user_id = g.current_user_id
    data = request.get_json() or {}

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    address_id = data.get('address_id')

    if not product_id or not address_id:
        return error_response('参数不完整')

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return error_response('数量必须大于0')
    except (TypeError, ValueError):
        return error_response('数量格式错误')

    user = db.session.get(User, user_id)
    if not user:
        return error_response('用户不存在', 404)

    product = db.session.get(Product, product_id)
    if not product or product.status != 1 or (product.exchange_points or 0) <= 0:
        return error_response('商品不可兑换')

    if product.available_stock < quantity:
        return error_response('库存不足')

    total_points = product.exchange_points * quantity
    if user.points < total_points:
        return error_response('积分不足')

    address = Address.query.filter_by(address_id=address_id, user_id=user_id).first()
    if not address:
        return error_response('地址不存在')

    # 生成订单（直接设为已支付，无需支付金额）
    order_id = generate_order_id()
    order = Order(
        order_id=order_id,
        user_id=user_id,
        total_amount=Decimal('0.00'),
        freight_amount=Decimal('0.00'),
        discount_amount=Decimal('0.00'),
        points_used=0,
        points_discount=Decimal('0.00'),
        payment_amount=Decimal('0.00'),
        status=1,  # 直接已支付
        payment_method=4,  # 4-积分兑换
        payment_time=datetime.now(),
        address_snapshot=json.dumps(address.to_dict(), ensure_ascii=False),
        buyer_note=f'积分兑换商品：{product.name} x{quantity}'
    )

    try:
        db.session.add(order)
        db.session.flush()

        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            product_name=product.name,
            product_image=product.main_image,
            price=Decimal('0.00'),
            quantity=quantity,
            subtotal=Decimal('0.00')
        )
        db.session.add(order_item)

        # 扣减积分
        user.points -= total_points
        points_log = PointsLog(
            user_id=user_id,
            type=2,
            amount=total_points,
            balance_after=user.points,
            source='EXCHANGE',
            source_id=str(order_id),
            description=f'积分兑换商品 {product.name} x{quantity}'
        )
        db.session.add(points_log)

        # 扣减库存
        product.stock -= quantity
        product.sold_count += quantity

        db.session.commit()
        return success_response({'order_id': str(order_id)}, '兑换成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'兑换失败: {str(e)}')


# ============ Refund ============

@order_bp.route('/<int:order_id>/refund', methods=['POST'])
@token_required
def apply_refund(order_id):
    order = Order.query.filter_by(order_id=order_id, user_id=g.current_user_id).first()
    if not order: return error_response('订单不存在', 404)
    if order.status not in (1, 3): return error_response('只能对已支付或已完成的订单申请退货')

    from app.models.models import Refund
    latest = Refund.query.filter_by(order_id=order_id).order_by(Refund.id.desc()).first()
    if latest and latest.status == 0: return error_response('已有待审核的退货申请')

    data = request.get_json() or {}
    reason = data.get('reason', '')
    if not reason.strip(): return error_response('请填写退货原因')

    try:
        order.status = 6
        order.refund_reason = reason
        refund = Refund(order_id=order_id, user_id=g.current_user_id, reason=reason)
        db.session.add(refund)
        db.session.commit()
        return success_response(message='退货申请已提交')
    except Exception as e:
        db.session.rollback()
        return error_response(f'提交失败: {str(e)}')


@order_bp.route('/refunds', methods=['GET'])
@token_required
def get_my_refunds():
    """Get user's refund list."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    q = Refund.query.filter_by(user_id=g.current_user_id).order_by(Refund.create_time.desc())
    return success_response(paginate(q, page, per_page))
