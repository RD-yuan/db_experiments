'''
Seckill routes.
'''
from flask import Blueprint, request, g
from app import db
from app.models.models import SeckillSession, SeckillProduct, Product, ProductSku, Order, OrderItem, Address, User
from app.utils.helpers import success_response, error_response, token_required, admin_required, generate_order_id
from datetime import datetime, timedelta
from decimal import Decimal
import json

seckill_bp = Blueprint('seckill', __name__)

# ---- Admin routes ----

@seckill_bp.route('/admin/seckill/sessions', methods=['GET'])
@admin_required
def list_sessions():
    sessions = SeckillSession.query.order_by(SeckillSession.start_time.desc()).all()
    return success_response([s.to_dict() for s in sessions])

@seckill_bp.route('/admin/seckill/sessions', methods=['POST'])
@admin_required
def create_session():
    data = request.get_json() or {}
    s = SeckillSession(
        name=data.get('name'),
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        status=data.get('status', 1)
    )
    db.session.add(s)
    db.session.commit()
    return success_response(s.to_dict(), '创建成功')

@seckill_bp.route('/admin/seckill/sessions/<int:sid>', methods=['PUT'])
@admin_required
def update_session(sid):
    s = db.session.get(SeckillSession, sid)
    if not s: return error_response('场次不存在', 404)
    data = request.get_json() or {}
    for f in ['name','start_time','end_time','status']:
        if f in data:
            if f in ('start_time','end_time'):
                setattr(s, f, datetime.fromisoformat(data[f]))
            else:
                setattr(s, f, data[f])
    db.session.commit()
    return success_response(s.to_dict())

# ---- User routes ----

@seckill_bp.route('/seckill/current', methods=['GET'])
def get_current():
    now = datetime.now()
    session = SeckillSession.query.filter(
        SeckillSession.start_time <= now,
        SeckillSession.end_time >= now,
        SeckillSession.status == 1
    ).first()
    if not session:
        return success_response({'session': None, 'products': []})
    products = SeckillProduct.query.filter_by(session_id=session.session_id).all()
    return success_response({
        'session': session.to_dict(),
        'products': [sp.to_dict() for sp in products]
    })

@seckill_bp.route('/seckill/orders', methods=['POST'])
@token_required
def create_seckill_order():
    data = request.get_json() or {}
    sp_id = data.get('seckill_product_id')
    quantity = int(data.get('quantity', 1))
    address_id = data.get('address_id')
    if quantity <= 0: return error_response('数量无效')

    user = db.session.get(User, g.current_user_id)
    if not user: return error_response('请先登录', 401)

    sp = db.session.get(SeckillProduct, sp_id)
    if not sp: return error_response('秒杀商品不存在', 404)

    session = sp.session
    now = datetime.now()
    if now < session.start_time or now > session.end_time or session.status != 1:
        return error_response('秒杀未开始或已结束')

    if sp.seckill_stock < quantity:
        return error_response('秒杀库存不足')

    # Check per-user limit
    existing = Order.query.join(OrderItem).filter(
        Order.user_id == user.user_id,
        OrderItem.product_id == sp.product_id,
        Order.status.in_([0,1,2,3]),
        Order.create_time >= session.start_time
    ).count()
    if existing + quantity > sp.limit_per_user:
        return error_response('超过限购数量')

    addr = Address.query.filter_by(address_id=address_id, user_id=user.user_id).first()
    if not addr: return error_response('地址不存在')

    try:
        sp.seckill_stock -= quantity
        sp.version += 1

        # Also reduce product stock
        product = sp.product
        if product:
            product.stock = max(0, (product.stock or 0) - quantity)
            product.sold_count = (product.sold_count or 0) + quantity
        product.sold_count = (product.sold_count or 0) + quantity
        if product and product.has_sku:
            skus = ProductSku.query.filter_by(product_id=product.product_id).all()
            for sc in skus:
                sc.locked_stock = max(0, (sc.locked_stock or 0) - quantity)

        order_id = generate_order_id()
        payment_amount = sp.seckill_price * quantity
        order = Order(
            order_id=order_id, user_id=user.user_id,
            total_amount=payment_amount, payment_amount=payment_amount,
            status=0, address_snapshot=json.dumps(addr.to_dict(), ensure_ascii=False)
        )
        db.session.add(order)
        db.session.flush()

        sp_product = sp.product
        item = OrderItem(
            order_id=order_id, product_id=sp_product.product_id,
            product_name=sp_product.name, product_image=sp_product.main_image,
            price=sp.seckill_price, quantity=quantity, subtotal=payment_amount
        )
        db.session.add(item)

        db.session.commit()
        return success_response({'order_id': str(order_id), 'payment_amount': float(payment_amount)}, '下单成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'下单失败: {str(e)}')
