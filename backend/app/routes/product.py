"""
商品路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import Product, Category, User, OrderItem, ShoppingCart, Review
from app.utils.helpers import (
    success_response, error_response, paginate,
    admin_required
)

product_bp = Blueprint('product', __name__)


@product_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['商品'],
    'summary': '获取商品列表',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 20},
        {'name': 'category_id', 'in': 'query', 'type': 'integer'},
        {'name': 'keyword', 'in': 'query', 'type': 'string'},
        {'name': 'min_price', 'in': 'query', 'type': 'number'},
        {'name': 'max_price', 'in': 'query', 'type': 'number'},
        {'name': 'sort', 'in': 'query', 'type': 'string', 'enum': ['price', 'sold', 'new']},
        {'name': 'order', 'in': 'query', 'type': 'string', 'enum': ['asc', 'desc'], 'default': 'desc'}
    ],
    'responses': {
        200: {'description': '商品列表'}
    }
})
def get_products():
    """获取商品列表（支持筛选、排序、分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', '')
    order = request.args.get('order', 'desc')
    
    # 手动解析 Token，判断管理员身份
    user = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split()[1]
        from app.utils.helpers import decode_token
        payload = decode_token(token)
        if payload:
            user = db.session.get(User, payload.get('user_id'))
    
    # 管理员可查看所有商品，普通用户仅看上架商品
    if user and user.is_admin:
        query = Product.query
    else:
        query = Product.query.filter(Product.status == 1)
    
    # 分类筛选
    if category_id:
        category_ids = [category_id]
        children = Category.query.filter_by(parent_id=category_id).all()
        category_ids.extend([c.category_id for c in children])
        query = query.filter(Product.category_id.in_(category_ids))
    
    # 关键词搜索
    if keyword:
        query = query.filter(Product.name.like(f'%{keyword}%'))
    
    # 价格区间
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # 排序
    if sort == 'price':
        query = query.order_by(
            Product.price.asc() if order == 'asc' else Product.price.desc()
        )
    elif sort == 'sold':
        query = query.order_by(
            Product.sold_count.asc() if order == 'asc' else Product.sold_count.desc()
        )
    elif sort == 'new':
        query = query.order_by(
            Product.create_time.asc() if order == 'asc' else Product.create_time.desc()
        )
    else:
        query = query.order_by(Product.create_time.desc())
    
    result = paginate(query, page, per_page)
    return success_response(result)


@product_bp.route('/<int:product_id>', methods=['GET'])
@swag_from({
    'tags': ['商品'],
    'summary': '获取商品详情',
    'parameters': [{'name': 'product_id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {200: {'description': '商品详情'}, 404: {'description': '商品不存在'}}
})
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)

    # 判断当前用户是否为管理员（允许查看下架商品）
    user = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split()[1]
        from app.utils.helpers import decode_token
        payload = decode_token(token)
        if payload:
            user = db.session.get(User, payload.get('user_id'))

    if not (user and user.is_admin) and product.status != 1:
        return error_response('商品不存在或已下架', 404)

    data = product.to_dict()
    if product.category_id:
        category = db.session.get(Category, product.category_id)
        data['category'] = category.to_dict() if category else None
    return success_response(data)


@product_bp.route('/hot', methods=['GET'])
@swag_from({
    'tags': ['商品'],
    'summary': '获取热销商品',
    'parameters': [{'name': 'limit', 'in': 'query', 'type': 'integer', 'default': 10}],
    'responses': {200: {'description': '热销商品列表'}}
})
def get_hot_products():
    limit = request.args.get('limit', 10, type=int)
    products = Product.query.filter(Product.status == 1, Product.is_hot == 1).order_by(Product.sold_count.desc()).limit(limit).all()
    return success_response([p.to_dict() for p in products])


@product_bp.route('/new', methods=['GET'])
@swag_from({
    'tags': ['商品'],
    'summary': '获取新品商品',
    'parameters': [{'name': 'limit', 'in': 'query', 'type': 'integer', 'default': 10}],
    'responses': {200: {'description': '新品商品列表'}}
})
def get_new_products():
    limit = request.args.get('limit', 10, type=int)
    products = Product.query.filter(Product.status == 1, Product.is_new == 1).order_by(Product.create_time.desc()).limit(limit).all()
    return success_response([p.to_dict() for p in products])

# ============ 积分兑换商品 ============

@product_bp.route('/exchange', methods=['GET'])
def get_exchange_products():
    """获取积分兑换商品列表（仅上架且设置了兑换积分的商品）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Product.query.filter(
        Product.exchange_points > 0,
        Product.status == 1
    ).order_by(Product.create_time.desc())

    result = paginate(query, page, per_page)
    return success_response(result)

# ============ 管理员接口 ============

@product_bp.route('', methods=['POST'])
@admin_required
@swag_from({
    'tags': ['商品管理'],
    'summary': '添加商品（管理员）',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'price': {'type': 'number'},
                'original_price': {'type': 'number'},
                'vip_price': {'type': 'number'},
                'stock': {'type': 'integer'},
                'category_id': {'type': 'integer'},
                'brand': {'type': 'string'},
                'main_image': {'type': 'string'}
            },
            'required': ['name', 'price', 'stock']
        }
    }],
    'responses': {200: {'description': '添加成功'}, 400: {'description': '参数错误'}}
})
def create_product():
    data = request.get_json()
    name = data.get('name', '').strip()
    price = data.get('price')
    stock = data.get('stock', 0)
    if not name:
        return error_response('商品名称不能为空')
    if price is None or price < 0:
        return error_response('价格无效')
    product = Product(
        name=name,
        description=data.get('description'),
        price=price,
        original_price=data.get('original_price'),
        vip_price=data.get('vip_price'),
        stock=stock,
        category_id=data.get('category_id'),
        brand=data.get('brand'),
        main_image=data.get('main_image'),
        sub_images=data.get('sub_images'),
        is_hot=data.get('is_hot', 0),
        is_new=data.get('is_new', 0),
        is_recommend=data.get('is_recommend', 0),
        exchange_points=data.get('exchange_points', 0)
    )
    try:
        db.session.add(product)
        db.session.commit()
        return success_response(product.to_dict(), '添加成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加失败: {str(e)}')


@product_bp.route('/<int:product_id>', methods=['PUT'])
@admin_required
@swag_from({
    'tags': ['商品管理'],
    'summary': '更新商品（管理员）',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'product_id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {'type': 'object'}}
    ],
    'responses': {200: {'description': '更新成功'}, 404: {'description': '商品不存在'}}
})
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)
    data = request.get_json()
    for field in ['name', 'description', 'price', 'original_price', 'vip_price',
                  'stock', 'category_id', 'brand', 'main_image', 'sub_images',
                  'status', 'is_hot', 'is_new', 'is_recommend', 'exchange_points']:
        if field in data:
            setattr(product, field, data[field])
    try:
        db.session.commit()
        return success_response(product.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """永久删除商品（仅当无关联订单）"""
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)

    if OrderItem.query.filter_by(product_id=product_id).count() > 0:
        return error_response('该商品已有订单记录，无法永久删除', 400)

    try:
        ShoppingCart.query.filter_by(product_id=product_id).delete()
        Review.query.filter_by(product_id=product_id).delete()
        db.session.delete(product)
        db.session.commit()
        return success_response(message='商品已永久删除')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}')