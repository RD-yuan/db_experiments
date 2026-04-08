"""
评价路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import Review, Order, OrderItem, Product
from app.utils.helpers import success_response, error_response, token_required, paginate

review_bp = Blueprint('review', __name__)


@review_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """获取商品评价"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Review.query.filter_by(product_id=product_id, status=1).order_by(
        Review.create_time.desc()
    )
    
    result = paginate(query, page, per_page)
    
    # 隐藏匿名用户信息
    for item in result['items']:
        if item.get('is_anonymous'):
            item['user_id'] = None
    
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
    'responses': {
        200: {'description': '评价成功'}
    }
})
def create_review():
    """提交评价"""
    user_id = g.current_user_id
    data = request.get_json()
    
    order_item_id = data.get('order_item_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    images = data.get('images', [])
    is_anonymous = data.get('is_anonymous', False)
    
    if not order_item_id or not rating:
        return error_response('参数不完整')
    
    if rating < 1 or rating > 5:
        return error_response('评分需在1-5之间')
    
    # 检查订单项
    order_item = db.session.get(OrderItem, order_item_id)
    if not order_item:
        return error_response('订单项不存在')
    
    # 检查订单归属
    order = db.session.get(Order, order_item.order_id)
    if not order or order.user_id != user_id:
        return error_response('无权评价')
    
    # 检查订单状态
    if order.status != 3:
        return error_response('只能评价已完成的订单')
    
    # 检查是否已评价
    if order_item.is_reviewed:
        return error_response('该商品已评价')
    
    review = Review(
        user_id=user_id,
        product_id=order_item.product_id,
        order_id=order.order_id,
        order_item_id=order_item_id,
        rating=rating,
        comment=comment,
        images=','.join(images) if images else None,
        is_anonymous=1 if is_anonymous else 0
    )
    
    try:
        order_item.is_reviewed = 1
        db.session.add(review)
        db.session.commit()
        return success_response(review.to_dict(), '评价成功')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'评价失败: {str(e)}')


@review_bp.route('/my', methods=['GET'])
@token_required
def get_my_reviews():
    """获取我的评价"""
    user_id = g.current_user_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Review.query.filter_by(user_id=user_id).order_by(
        Review.create_time.desc()
    )
    
    result = paginate(query, page, per_page)
    return success_response(result)
