# API 接口设计文档

## 1. 接口规范

### 1.1 基础URL
- 开发环境: `http://localhost:5000`
- 生产环境: 根据实际部署

### 1.2 认证方式
使用 JWT Bearer Token 认证：
```
Authorization: Bearer <token>
```

### 1.3 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

错误响应：
```json
{
    "code": 400,
    "message": "错误信息",
    "data": null
}
```

---

## 2. 认证模块

### 2.1 用户注册
```
POST /api/auth/register
```

**请求体：**
```json
{
    "username": "testuser",
    "password": "123456",
    "phone": "13800138000",
    "email": "test@example.com"
}
```

**响应：**
```json
{
    "code": 200,
    "message": "注册成功",
    "data": {
        "user": { ... },
        "token": "eyJ0eXAiOiJ..."
    }
}
```

### 2.2 用户登录
```
POST /api/auth/login
```

**请求体：**
```json
{
    "username": "testuser",
    "password": "123456"
}
```

**响应：**
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "user": { ... },
        "token": "eyJ0eXAiOiJ..."
    }
}
```

---

## 3. 商品模块

### 3.1 商品列表
```
GET /api/products?page=1&per_page=20&category_id=1&keyword=iPhone&sort=price&order=desc
```

**参数：**
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）
- `category_id`: 分类ID（可选）
- `keyword`: 搜索关键词（可选）
- `min_price`: 最低价格（可选）
- `max_price`: 最高价格（可选）
- `sort`: 排序字段（price/sold/new）
- `order`: 排序方式（asc/desc）

**响应：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5
    }
}
```

### 3.2 商品详情
```
GET /api/products/{product_id}
```

### 3.3 热销商品
```
GET /api/products/hot?limit=10
```

---

## 4. 购物车模块

### 4.1 查看购物车
```
GET /api/cart
Authorization: Bearer <token>
```

### 4.2 添加到购物车
```
POST /api/cart
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

### 4.3 更新数量
```
PUT /api/cart/{cart_id}
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "quantity": 3,
    "selected": 1
}
```

### 4.4 删除商品
```
DELETE /api/cart/{cart_id}
Authorization: Bearer <token>
```

---

## 5. 订单模块

### 5.1 创建订单
```
POST /api/orders
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "address_id": 1,
    "cart_ids": [1, 2, 3],
    "coupon_id": 1,
    "points_used": 100,
    "buyer_note": "请尽快发货"
}
```

### 5.2 订单列表
```
GET /api/orders?page=1&status=1
Authorization: Bearer <token>
```

### 5.3 订单详情
```
GET /api/orders/{order_id}
Authorization: Bearer <token>
```

### 5.4 支付订单（模拟）
```
POST /api/orders/{order_id}/pay
Authorization: Bearer <token>
```

### 5.5 取消订单
```
POST /api/orders/{order_id}/cancel
Authorization: Bearer <token>
```

### 5.6 确认收货
```
POST /api/orders/{order_id}/receive
Authorization: Bearer <token>
```

---

## 6. 优惠券模块

### 6.1 可领取的优惠券
```
GET /api/coupons/available
Authorization: Bearer <token>
```

### 6.2 我的优惠券
```
GET /api/coupons/my?status=0
Authorization: Bearer <token>
```

### 6.3 领取优惠券
```
POST /api/coupons/{coupon_id}/receive
Authorization: Bearer <token>
```

---

## 7. 评价模块

### 7.1 商品评价列表
```
GET /api/reviews/product/{product_id}?page=1&per_page=10
```

### 7.2 提交评价
```
POST /api/reviews
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "order_item_id": 1,
    "rating": 5,
    "comment": "非常好",
    "images": ["http://..."],
    "is_anonymous": false
}
```

---

## 8. 管理员模块

### 8.1 数据概览
```
GET /api/admin/stats/overview
Authorization: Bearer <token>
```

**响应：**
```json
{
    "code": 200,
    "data": {
        "total_users": 1000,
        "new_users_today": 15,
        "total_orders": 5000,
        "orders_today": 120,
        "total_sales": 150000.00,
        "today_sales": 3500.00,
        "total_products": 500
    }
}
```

### 8.2 热销商品Top10
```
GET /api/admin/stats/hot-products?limit=10
Authorization: Bearer <token>
```

### 8.3 销售趋势
```
GET /api/admin/stats/sales-trend?days=7
Authorization: Bearer <token>
```

### 8.4 发货
```
POST /api/admin/orders/{order_id}/ship
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "shipping_company": "顺丰速运",
    "shipping_number": "SF1234567890"
}
```

---

## 9. 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 参数错误 |
| 401 | 未授权（未登录或Token无效） |
| 403 | 禁止访问（无权限） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

_文档版本: 1.0_  
_最后更新: 2026-04-08_
