"""
Spec template and SKU routes.
"""
from flask import Blueprint, request
from app import db
from app.models.models import SpecTemplate, SpecValue, ProductSku, Product
from app.utils.helpers import success_response, error_response, admin_required
import json

spec_bp = Blueprint('spec', __name__)


@spec_bp.route('/spec-templates', methods=['GET'])
def get_spec_templates():
    """Get all spec templates with their values."""
    templates = SpecTemplate.query.order_by(SpecTemplate.template_id).all()
    return success_response([t.to_dict() for t in templates])


@spec_bp.route('/products/<int:product_id>/skus', methods=['PUT'])
@admin_required
def save_product_skus(product_id):
    """Admin: save SKU list for a product."""
    product = db.session.get(Product, product_id)
    if not product:
        return error_response('商品不存在', 404)

    data = request.get_json() or {}
    skus_data = data.get('skus', [])

    try:
        # Remove existing SKUs
        ProductSku.query.filter_by(product_id=product_id).delete()

        has_sku = 0
        for sku_item in skus_data:
            spec_ids = sku_item.get('spec_ids', [])
            if isinstance(spec_ids, list):
                spec_ids_str = json.dumps(spec_ids)
            else:
                spec_ids_str = str(spec_ids)

            # Build spec text from spec values with template names
            spec_values = SpecValue.query.filter(
                SpecValue.value_id.in_(spec_ids if isinstance(spec_ids, list) else json.loads(spec_ids_str))
            ).all()
            spec_text_parts = []
            for v in spec_values:
                tpl = db.session.get(SpecTemplate, v.template_id)
                if tpl:
                    spec_text_parts.append(f'{tpl.name}:{v.value}')
                else:
                    spec_text_parts.append(v.value)
            spec_text = ' / '.join(spec_text_parts)

            sku = ProductSku(
                product_id=product_id,
                spec_ids=spec_ids_str,
                spec_text=spec_text,
                price=sku_item.get('price'),
                stock=sku_item.get('stock', 0),
                image=sku_item.get('image'),
                status=sku_item.get('status', 1)
            )
            db.session.add(sku)
            has_sku = 1

        product.has_sku = has_sku
        product.stock = sum(s.get('stock', 0) for s in skus_data)
        db.session.commit()
        return success_response(message='SKU保存成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'保存失败: {str(e)}')

