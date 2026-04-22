"""
优惠券路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import Coupon, UserCoupon, User
from app.utils.helpers import success_response, error_response, token_required
from datetime import datetime

coupon_bp = Blueprint('coupon', __name__)


@coupon_bp.route('/available', methods=['GET'])
@token_required
@swag_from({
    'tags': ['优惠券'],
    'summary': '获取可领取的优惠券',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': '优惠券列表'}
    }
})
def get_available_coupons():
    """获取可领取的优惠券"""
    user = db.session.get(User, g.current_user_id)
    now = datetime.utcnow()
    
    # 查询可领取的优惠券
    coupons = Coupon.query.filter(
        Coupon.status == 1,
        Coupon.start_time <= now,
        Coupon.end_time >= now,
        Coupon.total_quantity.is_(None) | (Coupon.received_count < Coupon.total_quantity)
    ).all()
    
    # 检查用户是否已领取
    result = []
    for coupon in coupons:
        # VIP专属检查
        if coupon.is_vip_only and not user.is_vip:
            continue
        
        # 已领取数量检查
        received = UserCoupon.query.filter_by(
            user_id=user.user_id, coupon_id=coupon.coupon_id
        ).count()
        
        coupon_dict = coupon.to_dict()
        coupon_dict['received'] = received
        coupon_dict['can_receive'] = received < coupon.per_user_limit
        
        result.append(coupon_dict)
    
    return success_response(result)


@coupon_bp.route('/my', methods=['GET'])
@token_required
def get_my_coupons():
    """获取我的优惠券"""
    user_id = g.current_user_id
    status = request.args.get('status', 0, type=int)  # 0-未使用 1-已使用 2-已过期
    
    query = UserCoupon.query.filter_by(user_id=user_id, status=status)
    if status == 0:
        query = query.filter(UserCoupon.order_id.is_(None))
    user_coupons = query.order_by(UserCoupon.receive_time.desc()).all()
    
    return success_response([uc.to_dict() for uc in user_coupons])


@coupon_bp.route('/<int:coupon_id>/receive', methods=['POST'])
@token_required
def receive_coupon(coupon_id):
    """领取优惠券"""
    user = db.session.get(User, g.current_user_id)
    coupon = db.session.get(Coupon, coupon_id)
    
    if not coupon or coupon.status != 1:
        return error_response('优惠券不存在')
    
    now = datetime.utcnow()
    
    # 检查有效期
    if coupon.start_time > now or coupon.end_time < now:
        return error_response('优惠券不在有效期内')
    
    # VIP专属检查
    if coupon.is_vip_only and not user.is_vip:
        return error_response('此优惠券仅限VIP用户领取')
    
    # 检查库存
    if coupon.total_quantity and coupon.received_count >= coupon.total_quantity:
        return error_response('优惠券已领完')
    
    # 检查领取限制
    received = UserCoupon.query.filter_by(
        user_id=user.user_id, coupon_id=coupon_id
    ).count()
    
    if received >= coupon.per_user_limit:
        return error_response('已达领取上限')
    
    # 领取
    user_coupon = UserCoupon(
        user_id=user.user_id,
        coupon_id=coupon_id
    )
    
    try:
        coupon.received_count += 1
        db.session.add(user_coupon)
        db.session.commit()
        return success_response(user_coupon.to_dict(), '领取成功')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'领取失败: {str(e)}')
