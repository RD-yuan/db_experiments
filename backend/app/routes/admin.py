from flask import Blueprint, request, g, current_app
from flasgger import swag_from
from datetime import datetime, timedelta
from sqlalchemy import func
from decimal import Decimal
from app import db
from app.models.models import User, Product, Category, Order, OperationLog, OrderItem, PointsLog, ShoppingCart, Review, Coupon, UserCoupon, ProductSku
from app.routes.seckill import _restore_seckill_stock
from app.utils.helpers import (
    success_response, error_response, admin_required, paginate
)

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
    'responses': {200: {'description': '用户列表'}}
})
def get_users():
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
    data = request.get_json() or {}
    user = db.session.get(User, user_id)
    if not user:
        return error_response('用户不存在', 404)

    try:
        is_vip = int(data.get('is_vip', 0))
        vip_level = int(data.get('vip_level', 0))
        vip_months = int(data.get('vip_months', 0) or 0)
    except (TypeError, ValueError):
        return error_response('会员参数格式错误')

    if is_vip not in (0, 1):
        return error_response('会员状态无效')
    if is_vip and vip_level not in (1, 2, 3):
        return error_response('会员等级无效')
    if not is_vip and vip_level != 0:
        return error_response('取消会员时等级必须为0')
    if is_vip and vip_months <= 0:
        return error_response('会员有效期必须大于0个月')

    user.is_vip = is_vip
    user.vip_level = vip_level if is_vip else 0
    user.vip_expire_time = (
        datetime.now() + timedelta(days=vip_months * 30)
        if is_vip else None
    )

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
        order.shipping_time = datetime.now()
        db.session.commit()
        return success_response(message='发货成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'发货失败: {str(e)}')


# ============ 数据统计 ============

@admin_bp.route('/stats/overview', methods=['GET'])
@admin_required
def get_overview():
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    total_users = User.query.count()
    new_users_today = User.query.filter(User.create_time >= today_start).count()
    total_orders = Order.query.count()
    orders_today = Order.query.filter(Order.create_time >= today_start).count()
    today_sales = db.session.query(
        func.sum(Order.payment_amount)
    ).filter(
        Order.create_time >= today_start,
        Order.status.in_([1, 2, 3])
    ).scalar() or 0
    total_sales = db.session.query(
        func.sum(Order.payment_amount)
    ).filter(Order.status.in_([1, 2, 3])).scalar() or 0
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
    limit = request.args.get('limit', 10, type=int)
    products = Product.query.filter_by(status=1).order_by(Product.sold_count.desc()).limit(limit).all()
    return success_response([p.to_dict() for p in products])


@admin_bp.route('/stats/sales-trend', methods=['GET'])
@admin_required
def get_sales_trend():
    days = request.args.get('days', 7, type=int)
    start_date = datetime.now() - timedelta(days=days)
    result = db.session.query(
        func.date(Order.create_time).label('date'),
        func.count(Order.order_id).label('order_count'),
        func.sum(Order.payment_amount).label('sales_amount')
    ).filter(
        Order.create_time >= start_date,
        Order.status.in_([1, 2, 3])
    ).group_by(func.date(Order.create_time)).all()
    trend = [{
        'date': str(r.date),
        'order_count': r.order_count,
        'sales_amount': float(r.sales_amount or 0)
    } for r in result]
    return success_response(trend)


# ============ 商品管理 ============

@admin_bp.route('/products', methods=['GET'])
@admin_required
def get_admin_products():
    """管理员商品列表（包含下架商品）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    status = request.args.get('status', type=int)
    sort = request.args.get('sort', '')
    order = request.args.get('order', 'desc')

    query = Product.query

    if status is not None:
        query = query.filter(Product.status == status)

    if category_id:
        category_ids = [category_id]
        children = Category.query.filter_by(parent_id=category_id).all()
        category_ids.extend([c.category_id for c in children])
        query = query.filter(Product.category_id.in_(category_ids))

    if keyword:
        query = query.filter(Product.name.like(f'%{keyword}%'))

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == 'price':
        query = query.order_by(Product.price.asc() if order == 'asc' else Product.price.desc())
    elif sort == 'sold':
        query = query.order_by(Product.sold_count.asc() if order == 'asc' else Product.sold_count.desc())
    elif sort == 'new':
        query = query.order_by(Product.create_time.asc() if order == 'asc' else Product.create_time.desc())
    else:
        query = query.order_by(Product.create_time.desc())

    return success_response(paginate(query, page, per_page))


@admin_bp.route('/products/<int:product_id>/off-shelf', methods=['PUT'])
@admin_required
def off_shelf_product(product_id):
    """下架商品，并自动取消相关未完成订单（待支付/已支付）"""
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)
    if product.status == 0:
        return error_response('商品已是下架状态')

    try:
        product.status = 0

        # 查询包含该商品且状态为待支付(0)或已支付(1)的订单
        affected_orders = db.session.query(Order).join(OrderItem).filter(
            OrderItem.product_id == product_id,
            Order.status.in_([0, 1])
        ).distinct().all()

        for order in affected_orders:
            order_items = OrderItem.query.filter_by(order_id=order.order_id).all()

            if order.status == 1:  # 已支付订单退款
                user = order.user
                refund_amount = order.payment_amount or Decimal('0.00')
                user.balance = (user.balance or Decimal('0.00')) + refund_amount

                if order.points_used > 0:
                    user.points += order.points_used
                    points_log = PointsLog(
                        user_id=user.user_id,
                        type=1,
                        amount=order.points_used,
                        balance_after=user.points,
                        source='REFUND',
                        source_id=str(order.order_id),
                        description=f'订单 {order.order_id} 因商品下架退款退还积分'
                    )
                    db.session.add(points_log)

                for item in order_items:
                    item_product = item.product
                    if item_product:
                        if item.sku_id:
                            sku = db.session.get(ProductSku, item.sku_id)
                            if sku:
                                sku.stock = (sku.stock or 0) + item.quantity
                            all_skus = ProductSku.query.filter_by(product_id=item_product.product_id).all()
                            item_product.stock = sum((s.stock or 0) for s in all_skus)
                        else:
                            item_product.stock = (item_product.stock or 0) + item.quantity
                        item_product.sold_count = max(0, (item_product.sold_count or 0) - item.quantity)

            else:  # 待支付订单释放锁定库存
                for item in order_items:
                    item_product = item.product
                    if item_product:
                        if item.sku_id:
                            sku = db.session.get(ProductSku, item.sku_id)
                            if sku:
                                sku.locked_stock = max(0, (sku.locked_stock or 0) - item.quantity)
                            all_skus = ProductSku.query.filter_by(product_id=item_product.product_id).all()
                            item_product.locked_stock = sum(max(0, (s.locked_stock or 0)) for s in all_skus)
                        else:
                            item_product.locked_stock = max(0, (item_product.locked_stock or 0) - item.quantity)

            order.status = 4  # 已取消
            order.update_time = datetime.now()

        db.session.commit()
        return success_response(message='商品已下架，相关未完成订单已取消并退款')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'下架商品失败: {str(e)}')
        return error_response(f'下架失败: {str(e)}')


@admin_bp.route('/products/<int:product_id>/permanent', methods=['DELETE'])
@admin_required
def delete_product_permanently(product_id):
    """永久删除商品（仅当无关联订单记录）"""
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)

    order_item_count = OrderItem.query.filter_by(product_id=product_id).count()
    if order_item_count > 0:
        return error_response('该商品已有订单记录，无法永久删除，建议下架', 400)

    try:
        ShoppingCart.query.filter_by(product_id=product_id).delete()
        Review.query.filter_by(product_id=product_id).delete()
        db.session.delete(product)
        db.session.commit()
        return success_response(message='商品已永久删除')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}')


# ============ Enhanced Stats ============

@admin_bp.route('/stats/sales-chart', methods=['GET'])
@admin_required
def sales_chart():
    days = request.args.get('days', 30, type=int)
    start = datetime.now() - timedelta(days=days)
    rows = db.session.query(
        func.date(Order.create_time).label('date'),
        func.sum(Order.payment_amount).label('amount'),
        func.count(Order.order_id).label('count')
    ).filter(
        Order.create_time >= start,
        Order.status.in_([1, 2, 3])
    ).group_by(func.date(Order.create_time)).order_by('date').all()
    return success_response({
        'dates': [str(r.date) for r in rows],
        'amounts': [float(r.amount or 0) for r in rows],
        'counts': [r.count for r in rows]
    })

@admin_bp.route('/stats/product-rank', methods=['GET'])
@admin_required
def product_rank():
    limit = request.args.get('limit', 10, type=int)
    rows = db.session.query(
        Product.name, func.sum(OrderItem.quantity).label('qty'),
        func.sum(OrderItem.subtotal).label('sales')
    ).join(OrderItem, Product.product_id == OrderItem.product_id
    ).join(Order, OrderItem.order_id == Order.order_id
    ).filter(Order.status.in_([1, 2, 3])
    ).group_by(Product.product_id
    ).order_by(func.sum(OrderItem.quantity).desc()).limit(limit).all()
    return success_response([{'name': r.name, 'qty': r.qty, 'sales': float(r.sales or 0)} for r in rows])

@admin_bp.route('/stats/user-growth', methods=['GET'])
@admin_required
def user_growth():
    days = request.args.get('days', 30, type=int)
    start = datetime.now() - timedelta(days=days)
    rows = db.session.query(
        func.date(User.create_time).label('date'),
        func.count(User.user_id).label('count')
    ).filter(User.create_time >= start
    ).group_by(func.date(User.create_time)).order_by('date').all()
    return success_response({
        'dates': [str(r.date) for r in rows],
        'counts': [r.count for r in rows]
    })

@admin_bp.route('/stats/order-source', methods=['GET'])
@admin_required
def order_source():
    rows = db.session.query(
        Order.payment_method, func.count(Order.order_id)
    ).filter(Order.payment_method.isnot(None), Order.status.in_([1,2,3])
    ).group_by(Order.payment_method).all()
    mapping = {3: '余额', 4: '积分兑换'}
    return success_response([{'name': mapping.get(r[0], '其他'), 'value': r[1]} for r in rows])


# ============ Refund Management ============

@admin_bp.route('/refunds', methods=['GET'])
@admin_required
def list_refunds():
    from app.models.models import Refund
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', type=int)
    q = Refund.query.order_by(Refund.create_time.desc())
    if status is not None:
        q = q.filter_by(status=status)
    result = paginate(q, page, per_page)
    for item in result['items']:
        refund = db.session.get(Refund, item['id'])
        if refund and refund.order:
            item['order'] = refund.order.to_dict()
            item['username'] = refund.order.user.username if refund.order.user else ''
    return success_response(result)

@admin_bp.route('/refunds/<int:refund_id>', methods=['PUT'])
@admin_required
def process_refund(refund_id):
    from app.models.models import Refund, PointsLog
    data = request.get_json() or {}
    status = data.get('status')
    remark = data.get('remark', '')

    refund = db.session.get(Refund, refund_id)
    if not refund: return error_response('退货申请不存在', 404)
    if refund.status != 0: return error_response('该申请已处理')

    admin = db.session.get(User, g.current_user_id)

    try:
        if status == 1:  # Approve
            order = refund.order
            user = order.user
            original_status = order.status if order.status != 6 else 3  # 记录原始状态

            order.status = 5  # Refunded
            order.refund_remark = remark
            refund.status = 1
            refund.admin_id = admin.user_id
            refund.remark = remark

            # ---- POINTS CHECK FIRST ----
            earned = 0
            if order.payment_method != 4:
                earned = int(float(order.payment_amount))
                if user.has_active_vip():
                    benefits = current_app.config.get('VIP_BENEFITS', {}).get(user.vip_level, {})
                    rate = benefits.get('points_rate', 1.0)
                    earned = int(float(order.payment_amount) * rate)

            if earned > 0 and user.points < earned:
                # Auto-reject: insufficient points
                from app.models.models import Notification
                refund.status = 2
                refund.admin_id = admin.user_id
                refund.remark = f'积分不足：需扣除{earned}积分，当前仅{user.points}'
                order.status = 3 if order.receive_time else 1  # 恢复原状态
                order.refund_remark = refund.remark
                db.session.add(Notification(
                    title='退货申请未通过',
                    content=f'您的订单 {order.order_id} 退款需扣除 {earned} 赠送积分，但您当前仅剩 {user.points} 积分，无法退款。',
                    type=2, user_id=user.user_id
                ))
                db.session.commit()
                return error_response(message=f'积分不足无法退款：需扣除{earned}积分，当前仅{user.points}')

            # ---- PROCEED WITH REFUND ----
            # Return exchange points
            if order.payment_method == 4:
                log = PointsLog.query.filter_by(
                    user_id=user.user_id, source='EXCHANGE', source_id=str(order.order_id)
                ).first()
                if log:
                    user.points += log.amount
                    db.session.add(PointsLog(
                        user_id=user.user_id, type=1, amount=log.amount,
                        balance_after=user.points, source='REFUND',
                        source_id=str(order.order_id),
                        description='退货退还兑换积分'
                    ))

            # Refund balance
            refund_amount = order.payment_amount or Decimal('0.00')
            user.balance = (user.balance or Decimal('0.00')) + refund_amount

            # Refund used points
            if order.points_used > 0:
                user.points += order.points_used
                db.session.add(PointsLog(
                    user_id=user.user_id, type=1, amount=order.points_used,
                    balance_after=user.points, source='REFUND',
                    source_id=str(order.order_id),
                    description='退货退款退还积分'
                ))

            # Deduct earned points
            if earned > 0:
                user.points -= earned
                db.session.add(PointsLog(
                    user_id=user.user_id, type=2, amount=earned,
                    balance_after=user.points, source='REFUND',
                    source_id=str(order.order_id),
                    description='退货退款扣除赠送积分'
                ))

            # Restore stock
            for item in order.items:
                product = item.product
                if product:
                    if item.sku_id:
                        from app.models.models import ProductSku as PSku
                        sku = db.session.get(PSku, item.sku_id)
                        if sku:
                            sku.stock = (sku.stock or 0) + item.quantity
                        all_skus = PSku.query.filter_by(product_id=product.product_id).all()
                        product.stock = sum((s.stock or 0) for s in all_skus)
                    else:
                        product.stock = (product.stock or 0) + item.quantity
                    product.sold_count = max(0, (product.sold_count or 0) - item.quantity)

            _restore_seckill_stock(order)

            # Send approval notification
            from app.models.models import Notification
            db.session.add(Notification(
                title='退货申请已通过',
                content=f'您的订单 {order.order_id} 已退款。金额已退回余额。',
                type=2, user_id=user.user_id
            ))

            # Restore coupon
            from app.models.models import UserCoupon
            uc = UserCoupon.query.filter_by(order_id=order.order_id, status=1).first()
            if uc:
                uc.status = 0
                uc.use_time = None
                uc.order_id = None

        else:  # Reject
            refund.status = 2
            refund.admin_id = admin.user_id
            refund.remark = remark
            order = refund.order
            order.status = 3 if order.receive_time else 1  # 恢复原状态（有收货时间为已完成，否则已支付）
            order.refund_remark = remark

                # Send notification to user
        from app.models.models import Notification
        notify_title = '退货申请已处理'
        if status == 1:
            notify_content = '您的退货申请已通过，订单 ' + str(order.order_id) + ' 已退款。'
        else:
            notify_content = '您的退货申请未通过，原因：' + (remark or '无') + '。可重新申请。'
        db.session.add(Notification(title=notify_title, content=notify_content, type=2, user_id=order.user_id))
        db.session.commit()
        return success_response(message='处理完成')
    except Exception as e:
        db.session.rollback()
        return error_response(f'处理失败: {str(e)}')


# ============ Seckill Admin ============

@admin_bp.route('/seckill/products', methods=['GET'])
@admin_required
def list_seckill_products():
    from app.models.models import SeckillProduct
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = SeckillProduct.query.order_by(SeckillProduct.create_time.desc())
    return success_response(paginate(q, page, per_page))

@admin_bp.route('/seckill/products', methods=['POST'])
@admin_required
def add_seckill_product():
    from app.models.models import SeckillProduct, ProductSku
    data = request.get_json() or {}
    seckill_stock = data.get('seckill_stock', 0)
    sku_id = data.get('sku_id')

    product = db.session.get(Product, data['product_id'])
    if not product:
        return error_response('商品不存在', 404)

    # Validate stock
    if sku_id:
        sku = db.session.get(ProductSku, sku_id)
        if not sku or sku.product_id != product.product_id:
            return error_response('规格不存在')
        available = (sku.stock or 0) - (sku.locked_stock or 0)
        if seckill_stock > available:
            return error_response(f'秒杀库存({seckill_stock})不能超过规格可用库存({available})')
    else:
        available = (product.stock or 0) - (product.locked_stock or 0)
        if seckill_stock > available:
            return error_response(f'秒杀库存({seckill_stock})不能超过商品可用库存({available})')

    sp = SeckillProduct(
        session_id=data['session_id'],
        product_id=data['product_id'],
        sku_id=sku_id,
        seckill_price=data['seckill_price'],
        seckill_stock=seckill_stock,
        limit_per_user=data.get('limit_per_user', 1)
    )
    db.session.add(sp)

    # Lock stock (only increase locked_stock, do NOT decrease stock)
    if sku_id:
        sku.locked_stock = (sku.locked_stock or 0) + seckill_stock
    product.locked_stock = (product.locked_stock or 0) + seckill_stock

    db.session.commit()
    return success_response(sp.to_dict(), '添加成功')

@admin_bp.route('/seckill/products/<int:sp_id>', methods=['DELETE'])
@admin_required
def delete_seckill_product(sp_id):
    from app.models.models import SeckillProduct
    sp = db.session.get(SeckillProduct, sp_id)
    if sp:
        remaining = sp.seckill_stock
        if sp.sku_id:
            sku = db.session.get(ProductSku, sp.sku_id)
            if sku:
                sku.locked_stock = max(0, (sku.locked_stock or 0) - remaining)
        if sp.product:
            sp.product.locked_stock = max(0, (sp.product.locked_stock or 0) - remaining)
        db.session.delete(sp)
        db.session.commit()
    return success_response(message='已删除')


# ============ 优惠券管理 ============

@admin_bp.route('/coupons', methods=['GET'])
@admin_required
def admin_list_coupons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Coupon.query.order_by(Coupon.create_time.desc())
    return success_response(paginate(query, page, per_page))


@admin_bp.route('/coupons', methods=['POST'])
@admin_required
def admin_create_coupon():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return error_response('名称不能为空')
    try:
        coupon = Coupon(
            name=name,
            type=data.get('type', 1),
            value=data.get('value', 0),
            min_order_amount=data.get('min_order_amount', 0),
            total_quantity=data.get('total_quantity'),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else datetime.now(),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else datetime.now(),
        )
        db.session.add(coupon)
        db.session.commit()
        return success_response(coupon.to_dict(), '创建成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建失败: {str(e)}')


@admin_bp.route('/coupons/<int:coupon_id>', methods=['PUT'])
@admin_required
def admin_update_coupon(coupon_id):
    coupon = db.session.get(Coupon, coupon_id)
    if not coupon:
        return error_response('优惠券不存在', 404)
    data = request.get_json() or {}
    for field in ['name', 'type', 'value', 'min_order_amount', 'total_quantity', 'status', 'start_time', 'end_time']:
        if field in data:
            val = data[field]
            if field in ('start_time', 'end_time') and val and isinstance(val, str):
                val = datetime.fromisoformat(val)
            setattr(coupon, field, val)
    try:
        db.session.commit()
        return success_response(coupon.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')


@admin_bp.route('/coupons/<int:coupon_id>', methods=['DELETE'])
@admin_required
def admin_delete_coupon(coupon_id):
    coupon = db.session.get(Coupon, coupon_id)
    if not coupon:
        return error_response('优惠券不存在', 404)
    try:
        UserCoupon.query.filter_by(coupon_id=coupon_id).delete()
        db.session.delete(coupon)
        db.session.commit()
        return success_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}')
