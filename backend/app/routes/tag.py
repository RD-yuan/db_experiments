"""
Tag routes.
"""
from flask import Blueprint, request
from app import db
from app.models.models import Tag, ProductTag, Product
from app.utils.helpers import success_response, error_response, admin_required

tag_bp = Blueprint('tag', __name__)


@tag_bp.route('/tags', methods=['GET'])
def list_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return success_response([t.to_dict() for t in tags])


@tag_bp.route('/tags', methods=['POST'])
@admin_required
def create_tag():
    data = request.get_json() or {}
    name = (data.get('name', '') or '').strip()
    if not name:
        return error_response('标签名不能为空')
    if Tag.query.filter_by(name=name).first():
        return error_response('标签已存在')
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return success_response(tag.to_dict(), '创建成功')


@tag_bp.route('/products/<int:product_id>/tags', methods=['GET'])
def get_product_tags(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)
    ptags = ProductTag.query.filter_by(product_id=product_id).all()
    return success_response([{
        'tag_id': pt.tag_id,
        'name': pt.tag.name if pt.tag else ''
    } for pt in ptags])


@tag_bp.route('/products/<int:product_id>/tags', methods=['PUT'])
@admin_required
def set_product_tags(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)
    data = request.get_json() or {}
    tag_ids = data.get('tag_ids', [])

    try:
        ProductTag.query.filter_by(product_id=product_id).delete()
        for tid in tag_ids:
            tag = db.session.get(Tag, tid)
            if tag:
                db.session.add(ProductTag(product_id=product_id, tag_id=tid))
        db.session.commit()
        return success_response(message='标签更新成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}')
