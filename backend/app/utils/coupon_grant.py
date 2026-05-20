'''
Coupon auto-grant helper.
'''
from app import db
from app.models.models import Coupon, UserCoupon, User
from datetime import datetime
from flask import current_app


def grant_coupon_to_user(user_id, coupon_id):
    '''Grant coupon to user. Returns True on success, False if already claimed or unavailable.'''
    coupon = db.session.get(Coupon, coupon_id)
    if not coupon or coupon.status != 1:
        return False

    now = datetime.now()
    if coupon.start_time and coupon.start_time > now:
        return False
    if coupon.end_time and coupon.end_time < now:
        return False

    # Check per-user limit
    existing = UserCoupon.query.filter_by(user_id=user_id, coupon_id=coupon_id).count()
    if existing >= (coupon.per_user_limit or 1):
        return False

    # Check total quantity
    if coupon.total_quantity and (coupon.received_count or 0) >= coupon.total_quantity:
        return False

    # Check VIP only
    user = db.session.get(User, user_id)
    if coupon.is_vip_only and (not user or not user.has_active_vip()):
        return False

    try:
        coupon.received_count = (coupon.received_count or 0) + 1
        uc = UserCoupon(user_id=user_id, coupon_id=coupon_id, status=0)
        db.session.add(uc)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def grant_new_user_coupon(user_id):
    '''Grant new-user coupon (configurable via NEW_USER_COUPON_ID).'''
    coupon_id = current_app.config.get('NEW_USER_COUPON_ID', 1)
    grant_coupon_to_user(user_id, coupon_id)


def grant_order_amount_coupon(user_id, payment_amount):
    '''Grant order-amount coupon if threshold is met.'''
    threshold = current_app.config.get('ORDER_AMOUNT_THRESHOLD', 200)
    coupon_id = current_app.config.get('ORDER_AMOUNT_COUPON_ID', 2)
    if float(payment_amount) >= threshold:
        grant_coupon_to_user(user_id, coupon_id)
