"""
商品路由
"""
import uuid
from decimal import Decimal
from pathlib import Path
from flask import Blueprint, request, g
from sqlalchemy import func, select
from flasgger import swag_from
from app import db
from app.models.models import Product, Category, User, OrderItem, ShoppingCart, Review
from app.utils.helpers import (
    success_response, error_response, paginate,
    admin_required
)

product_bp = Blueprint('product', __name__)

ALLOWED_PRODUCT_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_PRODUCT_IMAGE_SIZE = 5 * 1024 * 1024


def _save_upload_image(file, filename_prefix='product'):
    if not file or not file.filename:
        return None, '请选择图片'

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_PRODUCT_IMAGE_EXTENSIONS:
        return None, '仅支持 png/jpg/jpeg/gif/webp'

    if request.content_length and request.content_length > MAX_PRODUCT_IMAGE_SIZE:
        return None, '图片大小不能超过 5MB'

    upload_dir = Path(__file__).resolve().parents[1] / 'static' / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{filename_prefix}_{uuid.uuid4().hex}.{ext}"
    filepath = upload_dir / filename
    file.save(str(filepath))
    return f"/static/uploads/{filename}", None


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
    
    # 关键词搜索（名称 / 描述 / 品牌 / 分类名 / 标签名）
    if keyword:
        from app.models.models import Tag, ProductTag

        # 匹配标签的商品 ID 子查询
        tag_match_subq = (
            db.session.query(ProductTag.product_id)
            .join(Tag, Tag.tag_id == ProductTag.tag_id)
            .filter(Tag.name.like(f'%{keyword}%'))
            .subquery()
        )

        keyword_filter = db.or_(
            Product.name.like(f'%{keyword}%'),
            Product.description.like(f'%{keyword}%'),
            Product.brand.like(f'%{keyword}%'),
            Product.product_id.in_(tag_match_subq)
        )

        # 分类名搜索需要 outerjoin Category
        query = query.outerjoin(Category, Product.category_id == Category.category_id)
        keyword_filter = db.or_(keyword_filter, Category.name.like(f'%{keyword}%'))
        query = query.filter(keyword_filter)
    
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
    elif sort == 'rating':
        avg_subq = (
            select(
                Review.product_id,
                func.coalesce(func.avg(Review.rating), 0).label('avg_rating'),
                func.count(Review.review_id).label('review_count')
            )
            .where(Review.status == 1)
            .group_by(Review.product_id)
            .subquery()
        )
        query = query.outerjoin(avg_subq, Product.product_id == avg_subq.c.product_id)
        query = query.order_by(
            avg_subq.c.avg_rating.desc() if order != 'asc' else avg_subq.c.avg_rating.asc()
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

    # 为每个商品附加平均评分
    if sort == 'rating' and result['items']:
        rating_map = {}
        product_ids = [p['product_id'] for p in result['items']]
        rating_rows = (
            db.session.query(
                Review.product_id,
                func.coalesce(func.avg(Review.rating), 0),
                func.count(Review.review_id)
            )
            .filter(Review.product_id.in_(product_ids), Review.status == 1)
            .group_by(Review.product_id)
            .all()
        )
        rating_map = {row[0]: (float(row[1]), row[2]) for row in rating_rows}
        for product_dict in result['items']:
            avg_rating, review_count = rating_map.get(product_dict['product_id'], (0, 0))
            product_dict['avg_rating'] = round(avg_rating, 1)
            product_dict['review_count'] = review_count
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

@product_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_product_image():
    """上传商品主图，返回 URL；传入 product_id 时直接写入商品主图字段。"""
    product_id = request.form.get('product_id', type=int)
    product = None
    if product_id:
        product = db.session.get(Product, product_id)
        if not product:
            return error_response('商品不存在', 404)

    file = request.files.get('file')
    url, error = _save_upload_image(file)
    if error:
        return error_response(error)

    if product:
        try:
            product.main_image = url
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return error_response(f'保存图片失败: {str(e)}')

    return success_response({'url': url}, '上传成功')


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

    # 如果修改了价格且未显式设置 original_price，自动将旧价格写入 original_price
    if 'price' in data:
        new_price = Decimal(str(data['price']))
        old_price = product.price
        if data.get('original_price') is None and old_price is not None and new_price != old_price:
            product.original_price = old_price
            data.pop('original_price', None)  # 防止下方循环覆盖为 None

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
