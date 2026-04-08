"""
分类路由
"""
from flask import Blueprint
from flasgger import swag_from
from app import db
from app.models.models import Category
from app.utils.helpers import success_response, error_response, admin_required

category_bp = Blueprint('category', __name__)


@category_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['分类'],
    'summary': '获取分类列表（树形结构）',
    'responses': {
        200: {'description': '分类列表'}
    }
})
def get_categories():
    """获取分类列表（树形结构）"""
    categories = Category.query.filter_by(status=1).order_by(Category.sort_order).all()
    
    # 构建树形结构
    def build_tree(parent_id=0):
        return [
            {
                **cat.to_dict(),
                'children': build_tree(cat.category_id)
            }
            for cat in categories
            if cat.parent_id == parent_id
        ]
    
    tree = build_tree()
    return success_response(tree)


@category_bp.route('/<int:category_id>', methods=['GET'])
@swag_from({
    'tags': ['分类'],
    'summary': '获取分类详情',
    'parameters': [
        {'name': 'category_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': '分类详情'},
        404: {'description': '分类不存在'}
    }
})
def get_category(category_id):
    """获取分类详情"""
    category = db.session.get(Category, category_id)
    
    if not category:
        return error_response('分类不存在', 404)
    
    return success_response(category.to_dict())


@category_bp.route('', methods=['POST'])
@admin_required
@swag_from({
    'tags': ['分类管理'],
    'summary': '添加分类（管理员）',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'parent_id': {'type': 'integer', 'default': 0},
                'icon': {'type': 'string'},
                'sort_order': {'type': 'integer', 'default': 0}
            },
            'required': ['name']
        }
    }],
    'responses': {
        200: {'description': '添加成功'}
    }
})
def create_category():
    """添加分类"""
    from flask import request
    
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return error_response('分类名称不能为空')
    
    parent_id = data.get('parent_id', 0)
    
    # 计算层级
    level = 1
    if parent_id > 0:
        parent = db.session.get(Category, parent_id)
        if parent:
            level = parent.level + 1
        else:
            return error_response('父分类不存在')
    
    category = Category(
        name=name,
        parent_id=parent_id,
        level=level,
        icon=data.get('icon'),
        sort_order=data.get('sort_order', 0)
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        return success_response(category.to_dict(), '添加成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加失败: {str(e)}')
