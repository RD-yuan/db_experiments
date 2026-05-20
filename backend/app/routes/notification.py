'''
Notification routes.
'''
from flask import Blueprint, request, g
from app import db
from app.models.models import Notification, User
from app.utils.helpers import success_response, error_response, token_required, admin_required, paginate
from sqlalchemy import or_

notif_bp = Blueprint('notification', __name__)

@notif_bp.route('/notifications', methods=['GET'])
@token_required
def list_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Notification.query.filter(
        or_(Notification.type == 1, Notification.user_id == g.current_user_id)
    ).order_by(Notification.create_time.desc())
    return success_response(paginate(query, page, per_page))

@notif_bp.route('/notifications/unread-count', methods=['GET'])
@token_required
def unread_count():
    count = Notification.query.filter(
        Notification.is_read == 0,
        or_(Notification.type == 1, Notification.user_id == g.current_user_id)
    ).count()
    return success_response({'count': count})

@notif_bp.route('/notifications/<int:nid>/read', methods=['PUT'])
@token_required
def mark_read(nid):
    n = Notification.query.filter(
        Notification.id == nid,
        or_(Notification.type == 1, Notification.user_id == g.current_user_id)
    ).first()
    if not n: return error_response('消息不存在', 404)
    n.is_read = 1
    db.session.commit()
    return success_response(message='已标记已读')

@notif_bp.route('/notifications/read-all', methods=['POST'])
@token_required
def read_all():
    Notification.query.filter(
        or_(Notification.type == 1, Notification.user_id == g.current_user_id)
    ).update({'is_read': 1}, synchronize_session=False)
    db.session.commit()
    return success_response(message='全部已读')

# Admin routes
@notif_bp.route('/admin/notifications', methods=['GET'])
@admin_required
def admin_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Notification.query.order_by(Notification.create_time.desc())
    return success_response(paginate(query, page, per_page))

@notif_bp.route('/admin/notifications', methods=['POST'])
@admin_required
def admin_create():
    data = request.get_json() or {}
    n = Notification(
        title=data['title'],
        content=data.get('content'),
        type=data.get('type', 1),
        user_id=data.get('user_id') if data.get('type') == 2 else None
    )
    db.session.add(n)
    db.session.commit()
    return success_response(n.to_dict(), '发布成功')
