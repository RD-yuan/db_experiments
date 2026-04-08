"""
购物车路由
"""
from flask import Blueprint, request, g
from flasgger import swag_from
from app import db
from app.models.models import ShoppingCart, Product
from app.utils.helpers import success_response, error_response, token_required

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('', methods=['GET'])
@token_required
@swag_from({
    'tags': ['购物车'],
    'summary': '获取购物车列表',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': '购物车列表'}
    }
})
def get_cart():
    """获取购物车列表"""
    user_id = g.current_user_id
    
    cart_items = ShoppingCart.query.filter_by(user_id=user_id).order_by(
        ShoppingCart.create_time.desc()
    ).all()
    
    # 计算总价
    total_amount = 0
    total_count = 0
    selected_count = 0
    
    for item in cart_items:
        if item.product and item.selected:
            total_amount += float(item.product.price) * item.quantity
            selected_count += item.quantity
        total_count += item.quantity
    
    return success_response({
        'items': [item.to_dict() for item in cart_items],
        'total_count': total_count,
        'selected_count': selected_count,
        'total_amount': round(total_amount, 2)
    })


@cart_bp.route('', methods=['POST'])
@token_required
@swag_from({
    'tags': ['购物车'],
    'summary': '添加商品到购物车',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'quantity': {'type': 'integer', 'default': 1}
            },
            'required': ['product_id']
        }
    }],
    'responses': {
        200: {'description': '添加成功'},
        400: {'description': '参数错误'}
    }
})
def add_to_cart():
    """添加商品到购物车"""
    user_id = g.current_user_id
    data = request.get_json()
    
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return error_response('商品ID不能为空')
    
    if quantity < 1:
        return error_response('数量必须大于0')
    
    # 检查商品
    product = db.session.get(Product, product_id)
    if not product or product.status != 1:
        return error_response('商品不存在或已下架')
    
    if product.available_stock < quantity:
        return error_response('库存不足')
    
    # 检查购物车是否已有该商品
    cart_item = ShoppingCart.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first()
    
    try:
        if cart_item:
            # 更新数量
            cart_item.quantity += quantity
            cart_item.selected = 1
        else:
            # 新增
            cart_item = ShoppingCart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return success_response(cart_item.to_dict(), '添加成功')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加失败: {str(e)}')


@cart_bp.route('/<int:cart_id>', methods=['PUT'])
@token_required
@swag_from({
    'tags': ['购物车'],
    'summary': '更新购物车商品数量',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'cart_id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'quantity': {'type': 'integer'},
                'selected': {'type': 'integer'}
            }
        }}
    ],
    'responses': {
        200: {'description': '更新成功'}
    }
})
def update_cart_item(cart_id):
    """更新购物车商品"""
    user_id = g.current_user_id
    data = request.get_json()
    
    cart_item = ShoppingCart.query.filter_by(
        cart_id=cart_id, user_id=user_id
    ).first()
    
    if not cart_item:
        return error_response('购物车项不存在', 404)
    
    if 'quantity' in data:
        quantity = data['quantity']
        if quantity < 1:
            return error_response('数量必须大于0')
        
        # 检查库存
        if cart_item.product and cart_item.product.available_stock < quantity:
            return error_response('库存不足')
        
        cart_item.quantity = quantity
    
    if 'selected' in data:
        cart_item.selected = data['selected']
    
    try:
        db.session.commit()
        return success_response(cart_item.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')


@cart_bp.route('/<int:cart_id>', methods=['DELETE'])
@token_required
@swag_from({
    'tags': ['购物车'],
    'summary': '删除购物车商品',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'cart_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': '删除成功'}
    }
})
def delete_cart_item(cart_id):
    """删除购物车商品"""
    user_id = g.current_user_id
    
    cart_item = ShoppingCart.query.filter_by(
        cart_id=cart_id, user_id=user_id
    ).first()
    
    if not cart_item:
        return error_response('购物车项不存在', 404)
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return success_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}')


@cart_bp.route('/clear', methods=['POST'])
@token_required
@swag_from({
    'tags': ['购物车'],
    'summary': '清空购物车',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': '清空成功'}
    }
})
def clear_cart():
    """清空购物车"""
    user_id = g.current_user_id
    
    try:
        ShoppingCart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return success_response(message='购物车已清空')
    except Exception as e:
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}')
