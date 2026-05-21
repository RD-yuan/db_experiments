"""
评价路由
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import Review, Order, OrderItem, Product, User
from app.utils.helpers import success_response, error_response, token_required, paginate, log_operation

review_bp = Blueprint('review', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


@review_bp.route('/upload-image', methods=['POST'])
@token_required
def upload_review_image():
    """上传评价/追评图片"""
    file = request.files.get('file')
    if not file or not file.filename:
        return error_response('请选择图片')
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return error_response('仅支持 png/jpg/jpeg/gif/webp')
    if request.content_length and request.content_length > MAX_IMAGE_SIZE:
        return error_response('图片不能超过 5MB')
    upload_dir = Path(__file__).resolve().parents[1] / 'static' / 'uploads' / 'reviews'
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"review_{uuid.uuid4().hex}.{ext}"
    filepath = upload_dir / filename
    file.save(str(filepath))
    return success_response({'url': f'/static/uploads/reviews/{filename}'}, '上传成功')


def _join_images(images):
    if not images:
        return None
    if isinstance(images, list):
        return json.dumps(images, ensure_ascii=False)
    return images


@review_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """获取商品评价，支持好评/差评筛选"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    rating_type = request.args.get('rating_type', '').strip()

    query = Review.query.filter_by(product_id=product_id, status=1)
    if rating_type == 'good':
        query = query.filter(Review.rating >= 4)
    elif rating_type == 'bad':
        query = query.filter(Review.rating <= 2)

    query = query.order_by(Review.create_time.desc())
    result = paginate(query, page, per_page)
    for item in result['items']:
        if item.get('is_anonymous'):
            item['username'] = '匿名用户'
    return success_response(result)


@review_bp.route('', methods=['POST'])
@token_required
@swag_from({
    'tags': ['评价'],
    'summary': '提交评价',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'order_item_id': {'type': 'integer'},
                'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                'comment': {'type': 'string'},
                'images': {'type': 'array', 'items': {'type': 'string'}},
                'is_anonymous': {'type': 'boolean'}
            },
            'required': ['order_item_id', 'rating']
        }
    }],
    'responses': {200: {'description': '评价成功'}}
})
def create_review():
    """提交评价（仅订单所属用户）"""
    user_id = g.current_user_id
    data = request.get_json()
    order_item_id = data.get('order_item_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    images = data.get('images', [])
    is_anonymous = data.get('is_anonymous', False)

    if not order_item_id or not rating:
        return error_response('参数不完整')
    if not 1 <= rating <= 5:
        return error_response('评分需在1-5之间')

    order_item = db.session.get(OrderItem, order_item_id)
    if not order_item:
        return error_response('订单项不存在')

    order = db.session.get(Order, order_item.order_id)
    if not order or order.user_id != user_id:
        return error_response('无权评价此订单')
    if order.status != 3:
        return error_response('只能评价已完成的订单')
    if order_item.is_reviewed:
        return error_response('该商品已评价，如需修改请使用更新接口')

    review = Review(
        user_id=user_id,
        product_id=order_item.product_id,
        order_id=order.order_id,
        order_item_id=order_item_id,
        rating=rating,
        comment=comment,
        images=_join_images(images),
        is_anonymous=1 if is_anonymous else 0
    )
    try:
        order_item.is_reviewed = 1
        db.session.add(review)
        db.session.commit()
        log_operation(user_id, 'CREATE_REVIEW', f'评价商品 #{order_item.product_id}，评分 {rating}')
        return success_response(review.to_dict(), '评价成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'评价失败: {str(e)}')


@review_bp.route('/<int:review_id>', methods=['PUT'])
@token_required
def update_review(review_id):
    """修改评价（仅限本人）"""
    user_id = g.current_user_id
    review = db.session.get(Review, review_id)
    if not review:
        return error_response('评价不存在', 404)
    if review.user_id != user_id:
        return error_response('无权修改他人评价', 403)

    data = request.get_json()
    if 'rating' in data:
        if not 1 <= data['rating'] <= 5:
            return error_response('评分需在1-5之间')
        review.rating = data['rating']
    if 'comment' in data:
        review.comment = data['comment']
    if 'images' in data:
        review.images = _join_images(data['images'])
    if 'is_anonymous' in data:
        review.is_anonymous = 1 if data['is_anonymous'] else 0

    try:
        db.session.commit()
        return success_response(review.to_dict(), '评价已更新')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')


@review_bp.route('/<int:review_id>/follow-up', methods=['PUT'])
@token_required
def add_follow_up(review_id):
    """追加评价（仅限本人，已完成订单）"""
    user_id = g.current_user_id
    review = db.session.get(Review, review_id)
    if not review:
        return error_response('评价不存在', 404)
    if review.user_id != user_id:
        return error_response('无权操作他人评价', 403)
    if review.follow_up_comment:
        return error_response('已追评过，不可重复追评')

    data = request.get_json() or {}
    comment = (data.get('comment') or '').strip()
    images = data.get('images', [])
    if not comment:
        return error_response('追评内容不能为空')

    review.follow_up_comment = comment
    review.follow_up_images = _join_images(images)
    review.follow_up_time = datetime.now()

    try:
        db.session.commit()
        return success_response(review.to_dict(), '追评成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'追评失败: {str(e)}')


@review_bp.route('/<int:review_id>', methods=['DELETE'])
@token_required
def delete_review(review_id):
    """删除评价（仅限本人，同时重置订单项评价状态）"""
    user_id = g.current_user_id
    review = db.session.get(Review, review_id)
    if not review:
        return error_response('评价不存在', 404)
    if review.user_id != user_id:
        return error_response('无权删除他人评价', 403)

    try:
        order_item = db.session.get(OrderItem, review.order_item_id)
        if order_item:
            order_item.is_reviewed = 0
        db.session.delete(review)
        db.session.commit()
        log_operation(user_id, 'DELETE_REVIEW', f'删除评价 #{review_id}')
        return success_response(message='评价已删除')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}')


@review_bp.route('/my', methods=['GET'])
@token_required
def get_my_reviews():
    user_id = g.current_user_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = Review.query.filter_by(user_id=user_id).order_by(Review.create_time.desc())
    result = paginate(query, page, per_page)
    return success_response(result)
