'''
Notification routes.
'''
from flask import Blueprint, request, g
from app import db
from app.models.models import Notification, NotificationRead
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
    result = paginate(query, page, per_page)

    announcement_ids = [
        item['id'] for item in result['items']
        if item.get('type') == 1
    ]
    read_ids = set()
    if announcement_ids:
        rows = NotificationRead.query.filter(
            NotificationRead.user_id == g.current_user_id,
            NotificationRead.notification_id.in_(announcement_ids)
        ).all()
        read_ids = {row.notification_id for row in rows}

    for item in result['items']:
        if item.get('type') == 1:
            item['is_read'] = 1 if item['id'] in read_ids else 0

    return success_response(result)

@notif_bp.route('/notifications/unread-count', methods=['GET'])
@token_required
def unread_count():
    read_subq = db.session.query(NotificationRead.notification_id).filter(
        NotificationRead.user_id == g.current_user_id
    )
    announcement_count = Notification.query.filter(
        Notification.type == 1,
        ~Notification.id.in_(read_subq)
    ).count()
    personal_count = Notification.query.filter_by(
        type=2,
        user_id=g.current_user_id,
        is_read=0
    ).count()
    count = announcement_count + personal_count
    return success_response({'count': count})

@notif_bp.route('/notifications/<int:nid>/read', methods=['PUT'])
@token_required
def mark_read(nid):
    n = Notification.query.filter(
        Notification.id == nid,
        or_(Notification.type == 1, Notification.user_id == g.current_user_id)
    ).first()
    if not n: return error_response('消息不存在', 404)
    if n.type == 1:
        exists = NotificationRead.query.filter_by(
            notification_id=n.id,
            user_id=g.current_user_id
        ).first()
        if not exists:
            db.session.add(NotificationRead(notification_id=n.id, user_id=g.current_user_id))
    else:
        n.is_read = 1
    db.session.commit()
    return success_response(message='已标记已读')

@notif_bp.route('/notifications/read-all', methods=['POST'])
@token_required
def read_all():
    read_subq = db.session.query(NotificationRead.notification_id).filter(
        NotificationRead.user_id == g.current_user_id
    )
    unread_announcements = Notification.query.filter(
        Notification.type == 1,
        ~Notification.id.in_(read_subq)
    ).all()
    for notification in unread_announcements:
        db.session.add(NotificationRead(
            notification_id=notification.id,
            user_id=g.current_user_id
        ))

    Notification.query.filter_by(
        type=2,
        user_id=g.current_user_id,
        is_read=0
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
    title = (data.get('title') or '').strip()
    if not title:
        return error_response('标题不能为空')
    notification_type = int(data.get('type', 1) or 1)
    if notification_type not in (1, 2):
        return error_response('消息类型无效')
    if notification_type == 2 and not data.get('user_id'):
        return error_response('个人消息必须指定用户')

    n = Notification(
        title=title,
        content=data.get('content'),
        type=notification_type,
        user_id=data.get('user_id') if notification_type == 2 else None
    )
    db.session.add(n)
    db.session.commit()
    return success_response(n.to_dict(), '发布成功')
