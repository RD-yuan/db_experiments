"""
SQLAlchemy 数据模型
"""
from datetime import datetime
from app import db


class User(db.Model):
    """用户表"""
    __tablename__ = 't_user'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True)
    avatar = db.Column(db.String(255))
    gender = db.Column(db.SmallInteger, default=0)  # 0-未知 1-男 2-女
    birthday = db.Column(db.Date)
    is_vip = db.Column(db.SmallInteger, default=0)
    vip_level = db.Column(db.SmallInteger, default=0)
    vip_expire_time = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=0)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.SmallInteger, default=1)  # 0-禁用 1-正常
    last_login_time = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_admin = db.Column(db.SmallInteger, default=0)  # 0-普通用户 1-管理员
    
    # 关联
    addresses = db.relationship('Address', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    cart_items = db.relationship('ShoppingCart', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    user_coupons = db.relationship('UserCoupon', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    points_logs = db.relationship('PointsLog', backref='user', lazy='dynamic')

    VIP_LEVEL_TEXT = {
        0: '非会员',
        1: '银卡',
        2: '金卡',
        3: '钻石卡',
    }

    def has_active_vip(self):
        """Stored VIP flags only grant pricing benefits before expiry."""
        if not self.is_vip or not self.vip_level:
            return False
        if self.vip_expire_time and self.vip_expire_time <= datetime.utcnow():
            return False
        return True
    
    def to_dict(self):
        vip_active = self.has_active_vip()
        vip_level = self.vip_level if vip_active else 0
        return {
            'user_id': self.user_id,
            'username': self.username,
            'phone': self.phone,
            'email': self.email,
            'avatar': self.avatar,
            'gender': self.gender,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'is_vip': self.is_vip,
            'vip_level': self.vip_level,
            'vip_active': vip_active,
            'vip_level_text': self.VIP_LEVEL_TEXT.get(vip_level, '非会员'),
            'vip_expire_time': self.vip_expire_time.isoformat() if self.vip_expire_time else None,
            'points': self.points,
            'balance': float(self.balance) if self.balance else 0, # 新增返回余额
            'status': self.status,
            'is_admin': bool(self.is_admin),
            'create_time': self.create_time.isoformat() if self.create_time else None
        }


class Category(db.Model):
    """商品分类表"""
    __tablename__ = 't_category'
    
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('t_category.category_id'), default=0)
    level = db.Column(db.SmallInteger, default=1)
    icon = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    products = db.relationship('Product', backref='category', lazy='dynamic')
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[category_id]), lazy='dynamic')
    
    def to_dict(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'parent_id': self.parent_id,
            'level': self.level,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'status': self.status
        }


class Product(db.Model):
    """商品表"""
    __tablename__ = 't_product'
    
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    vip_price = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer, nullable=False, default=0)
    locked_stock = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    sold_count = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    category_id = db.Column(db.Integer, db.ForeignKey('t_category.category_id'))
    brand = db.Column(db.String(100))
    main_image = db.Column(db.String(255))
    sub_images = db.Column(db.Text)  # JSON数组
    status = db.Column(db.SmallInteger, default=1)  # 0-下架 1-上架
    is_hot = db.Column(db.SmallInteger, default=0)
    is_new = db.Column(db.SmallInteger, default=0)
    is_recommend = db.Column(db.SmallInteger, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    exchange_points = db.Column(db.Integer, default=0)
    
    # 关联
    reviews = db.relationship('Review', backref='product', lazy='dynamic')
    
    @property
    def available_stock(self):
        """可售库存"""
        return (self.stock or 0) - (self.locked_stock or 0)
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'original_price': float(self.original_price) if self.original_price else None,
            'vip_price': float(self.vip_price) if self.vip_price else None,
            'stock': self.stock or 0,
            'available_stock': self.available_stock,
            'sold_count': self.sold_count or 0,
            'category_id': self.category_id,
            'brand': self.brand,
            'main_image': self.main_image,
            'status': self.status if self.status is not None else 0,
            'is_hot': self.is_hot or 0,
            'is_new': self.is_new or 0,
            'is_recommend': self.is_recommend or 0,
            'exchange_points': self.exchange_points or 0 
        }


class Address(db.Model):
    """收货地址表"""
    __tablename__ = 't_address'
    
    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.user_id'), nullable=False)
    recipient_name = db.Column(db.String(50), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50))
    detail_address = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(20))
    is_default = db.Column(db.SmallInteger, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        # 安全获取字符串值，避免 None
        province = self.province or ''
        city = self.city or ''
        district = self.district or ''
        detail = self.detail_address or ''

        # 处理省级后缀
        if province:
            if province not in ('北京市', '天津市', '上海市', '重庆市', '香港特别行政区', '澳门特别行政区') and not province.endswith('省'):
                province += '省'
        # 处理市级后缀
        if city:
            if city not in ('北京市', '天津市', '上海市', '重庆市') and not city.endswith('市'):
                city += '市'
        # 处理区级后缀
        if district:
            if not (district.endswith('区') or district.endswith('县')):
                district += '区'

        full_addr = f"{province}{city}{district}{detail}"

        return {
            'address_id': self.address_id,
            'recipient_name': self.recipient_name,
            'recipient_phone': self.recipient_phone,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'detail_address': self.detail_address,
            'postal_code': self.postal_code,
            'is_default': self.is_default,
            'full_address': full_addr
        }


class ShoppingCart(db.Model):
    """购物车表"""
    __tablename__ = 't_shopping_cart'
    
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('t_product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    selected = db.Column(db.SmallInteger, default=1)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    product = db.relationship('Product', backref='cart_items')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uk_user_product'),
    )
    
    def to_dict(self):
        return {
            'cart_id': self.cart_id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'selected': self.selected
        }


class Coupon(db.Model):
    """优惠券表"""
    __tablename__ = 't_coupon'
    
    coupon_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False)  # 1-满减 2-折扣 3-代金
    value = db.Column(db.Numeric(10, 2), nullable=False)
    min_order_amount = db.Column(db.Numeric(10, 2), default=0)
    max_discount = db.Column(db.Numeric(10, 2))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_quantity = db.Column(db.Integer)
    received_count = db.Column(db.Integer, default=0)
    per_user_limit = db.Column(db.Integer, default=1)
    is_vip_only = db.Column(db.SmallInteger, default=0)
    status = db.Column(db.SmallInteger, default=1)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'coupon_id': self.coupon_id,
            'name': self.name,
            'type': self.type,
            'value': float(self.value),
            'min_order_amount': float(self.min_order_amount) if self.min_order_amount else 0,
            'max_discount': float(self.max_discount) if self.max_discount else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_vip_only': self.is_vip_only,
            'status': self.status
        }


class UserCoupon(db.Model):
    """用户优惠券表"""
    __tablename__ = 't_user_coupon'
    
    user_coupon_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.user_id'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('t_coupon.coupon_id'), nullable=False)
    status = db.Column(db.SmallInteger, default=0)  # 0-未使用 1-已使用 2-已过期
    receive_time = db.Column(db.DateTime, default=datetime.utcnow)
    use_time = db.Column(db.DateTime)
    order_id = db.Column(db.BigInteger)
    
    # 关联
    coupon = db.relationship('Coupon', backref='user_coupons')
    
    def to_dict(self):
        result = {
            'user_coupon_id': self.user_coupon_id,
            'status': self.status,
            'receive_time': self.receive_time.isoformat() if self.receive_time else None,
            'use_time': self.use_time.isoformat() if self.use_time else None
        }
        if self.coupon:
            result['coupon'] = self.coupon.to_dict()
        return result


class Order(db.Model):
    """订单表"""
    __tablename__ = 't_order'
    
    order_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.user_id'), nullable=False)
    
    # 金额信息
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    freight_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    points_used = db.Column(db.Integer, default=0)
    points_discount = db.Column(db.Numeric(10, 2), default=0)
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # 状态
    status = db.Column(db.SmallInteger, default=0)  # 0-待支付 1-已支付 2-已发货 3-已完成 4-已取消 5-已退款
    
    # 支付信息
    payment_method = db.Column(db.SmallInteger)  # 1-微信 2-支付宝 3-余额
    payment_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(100))
    
    # 物流信息
    shipping_company = db.Column(db.String(50))
    shipping_number = db.Column(db.String(100))
    shipping_time = db.Column(db.DateTime)
    receive_time = db.Column(db.DateTime)
    
    # 地址快照
    address_snapshot = db.Column(db.Text)
    
    # 备注
    buyer_note = db.Column(db.String(255))
    seller_note = db.Column(db.String(255))
    
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    STATUS_TEXT = {
        0: '待支付',
        1: '已支付',
        2: '已发货',
        3: '已完成',
        4: '已取消',
        5: '已退款'
    }
    
    def to_dict(self):
        return {
            'order_id': str(self.order_id),  # 关键修改：转为字符串，避免前端精度丢失
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'freight_amount': float(self.freight_amount) if self.freight_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'points_used': self.points_used,
            'points_discount': float(self.points_discount) if self.points_discount else 0,
            'payment_amount': float(self.payment_amount),
            'status': self.status,
            'status_text': self.STATUS_TEXT.get(self.status, '未知'),
            'payment_method': self.payment_method,
            'payment_time': self.payment_time.isoformat() if self.payment_time else None,
            'shipping_company': self.shipping_company,
            'shipping_number': self.shipping_number,
            'shipping_time': self.shipping_time.isoformat() if self.shipping_time else None,
            'address_snapshot': self.address_snapshot,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }


class OrderItem(db.Model):
    """订单明细表"""
    __tablename__ = 't_order_item'
    
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('t_order.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('t_product.product_id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    is_reviewed = db.Column(db.SmallInteger, default=0)
    
    # 关联
    product = db.relationship('Product')
    
    def to_dict(self):
        return {
            'order_item_id': self.order_item_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_image': self.product_image,
            'price': float(self.price),
            'quantity': self.quantity,
            'subtotal': float(self.subtotal),
            'is_reviewed': self.is_reviewed
        }


class Review(db.Model):
    """评价表"""
    __tablename__ = 't_review'
    
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('t_product.product_id'), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey('t_order.order_id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('t_order_item.order_item_id'), unique=True, nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON数组
    is_anonymous = db.Column(db.SmallInteger, default=0)
    status = db.Column(db.SmallInteger, default=1)  # 0-待审核 1-已发布 2-已屏蔽
    admin_reply = db.Column(db.Text)
    reply_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'order_item_id': self.order_item_id,
            'rating': self.rating,
            'comment': self.comment,
            'images': self.images,
            'is_anonymous': self.is_anonymous,
            'status': self.status,
            'admin_reply': self.admin_reply,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'username': self.user.username if self.user else '未知用户'
        }


class PointsLog(db.Model):
    """积分流水表"""
    __tablename__ = 't_points_log'
    
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.user_id'), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False)  # 1-收入 2-支出
    amount = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(50))
    source_id = db.Column(db.String(100))
    description = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'type': self.type,
            'type_text': '收入' if self.type == 1 else '支出',
            'amount': self.amount,
            'balance_after': self.balance_after,
            'source': self.source,
            'description': self.description,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }


class OperationLog(db.Model):
    """操作日志表"""
    __tablename__ = 't_operation_log'
    
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    user_type = db.Column(db.SmallInteger, default=1)  # 1-普通用户 2-管理员
    operation_type = db.Column(db.String(50), nullable=False)
    operation_desc = db.Column(db.String(255))
    request_method = db.Column(db.String(10))
    request_url = db.Column(db.String(255))
    request_params = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    result = db.Column(db.SmallInteger, default=1)  # 0-失败 1-成功
    error_msg = db.Column(db.Text)
    execute_time = db.Column(db.Integer)  # 毫秒
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
