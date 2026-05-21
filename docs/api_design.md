# API 接口设计文档

> 本文档按当前 `dev` 分支代码整理，接口以 Flask 蓝图注册路径和前端 `frontend/src/api/index.js` 调用为准。

## 1. 接口规范

### 1.1 基础 URL

| 环境 | 地址 |
|------|------|
| 后端开发环境 | `http://localhost:5000` |
| 前端开发代理 | `http://localhost:8080` 或当前启动端口 |

### 1.2 认证方式

受保护接口使用 JWT Bearer Token：

```http
Authorization: Bearer <token>
```

管理员接口在登录用户身份基础上继续校验 `is_admin` 标识。

### 1.3 统一响应格式

成功响应：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
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

分页接口统一返回：

```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

## 2. 认证模块

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/auth/register` | 否 | 用户注册，支持用户名、密码、手机号、邮箱 |
| POST | `/api/auth/login` | 否 | 用户登录，返回用户信息和 JWT |
| POST | `/api/auth/logout` | 是 | 用户退出登录 |

注册请求示例：

```json
{
  "username": "testuser",
  "password": "123456",
  "phone": "13800138000",
  "email": "test@example.com"
}
```

登录成功响应示例：

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "user_id": 1,
      "username": "testuser",
      "is_admin": 0,
      "is_vip": 0
    },
    "token": "jwt-token"
  }
}
```

## 3. 用户与会员模块

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/user/profile` | 是 | 获取个人资料 |
| PUT | `/api/user/profile` | 是 | 更新个人资料 |
| POST | `/api/user/avatar` | 是 | 上传头像 |
| GET | `/api/user/addresses` | 是 | 查询收货地址 |
| POST | `/api/user/addresses` | 是 | 新增收货地址 |
| PUT | `/api/user/addresses/{address_id}` | 是 | 修改收货地址 |
| DELETE | `/api/user/addresses/{address_id}` | 是 | 删除收货地址 |
| POST | `/api/user/recharge` | 是 | 余额充值 |
| GET | `/api/user/points` | 是 | 查询积分流水 |
| GET | `/api/user/consumption-stats` | 是 | 查询消费统计 |
| GET | `/api/user/vip/packages` | 是 | 查询 VIP 套餐 |
| POST | `/api/user/vip/purchase` | 是 | 购买或续费 VIP |

地址请求示例：

```json
{
  "recipient_name": "张三",
  "recipient_phone": "13800138000",
  "province": "广东省",
  "city": "深圳市",
  "district": "南山区",
  "detail_address": "科技园 1 号",
  "is_default": 1
}
```

## 4. 商品、分类、标签与规格模块

### 4.1 商品与分类

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/categories` | 否 | 查询分类树 |
| GET | `/api/categories/{category_id}` | 否 | 查询分类详情 |
| POST | `/api/categories` | 管理员 | 新增分类 |
| GET | `/api/products` | 可选 | 商品分页列表，普通用户仅看上架商品，管理员可看全部 |
| GET | `/api/products/{product_id}` | 可选 | 商品详情 |
| GET | `/api/products/hot` | 否 | 热销商品 |
| GET | `/api/products/new` | 否 | 新品商品 |
| GET | `/api/products/exchange` | 否 | 积分兑换商品 |
| POST | `/api/products` | 管理员 | 新增商品 |
| PUT | `/api/products/{product_id}` | 管理员 | 修改商品 |
| DELETE | `/api/products/{product_id}` | 管理员 | 逻辑删除商品 |

商品列表查询参数：

| 参数 | 说明 |
|------|------|
| `page` / `per_page` | 分页参数 |
| `category_id` | 分类筛选，包含一级子分类 |
| `keyword` | 名称、描述、品牌、分类名、标签名搜索 |
| `min_price` / `max_price` | 价格区间 |
| `sort` | `price`、`sold`、`new`、`rating` |
| `order` | `asc` 或 `desc` |

### 4.2 商品标签

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/tags` | 否 | 查询标签列表 |
| POST | `/api/tags` | 管理员 | 创建标签 |
| GET | `/api/products/{product_id}/tags` | 否 | 查询商品标签 |
| PUT | `/api/products/{product_id}/tags` | 管理员 | 设置商品标签 |

标签设置请求示例：

```json
{
  "tag_ids": [1, 2, 5]
}
```

### 4.3 规格模板与 SKU

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/spec-templates` | 否 | 查询规格模板与规格值 |
| PUT | `/api/products/{product_id}/skus` | 管理员 | 保存商品 SKU 列表 |

SKU 保存请求示例：

```json
{
  "skus": [
    {
      "spec_ids": [1, 4],
      "price": 2999.00,
      "stock": 20,
      "image": "/uploads/sku-red.jpg",
      "status": 1
    }
  ]
}
```

保存 SKU 时会同步更新商品 `has_sku` 和商品总库存。购物车、订单、秒杀均使用 `sku_id = 0` 表示无规格商品，非 0 表示指定 SKU。

## 5. 购物车模块

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/cart` | 是 | 查询购物车 |
| POST | `/api/cart` | 是 | 添加商品到购物车 |
| PUT | `/api/cart/{cart_id}` | 是 | 修改数量或选中状态 |
| DELETE | `/api/cart/{cart_id}` | 是 | 删除购物车项 |
| POST | `/api/cart/clear` | 是 | 清空购物车 |

添加购物车请求示例：

```json
{
  "product_id": 10,
  "sku_id": 25,
  "quantity": 2
}
```

校验规则：

- 多规格商品必须传入有效 `sku_id`。
- 同一用户、同一商品、同一 `sku_id` 在购物车中只保留一行。
- 库存校验使用商品或 SKU 的可用库存，即 `stock - locked_stock`。

## 6. 订单、支付、积分与退货模块

### 6.1 普通订单

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/orders` | 是 | 查询我的订单 |
| GET | `/api/orders/{order_id}` | 是 | 查询订单详情 |
| POST | `/api/orders` | 是 | 从购物车创建订单 |
| POST | `/api/orders/{order_id}/cancel` | 是 | 取消未支付订单 |
| POST | `/api/orders/{order_id}/pay` | 是 | 余额支付订单 |
| POST | `/api/orders/{order_id}/receive` | 是 | 确认收货 |
| POST | `/api/orders/exchange` | 是 | 创建积分兑换订单 |

创建订单请求示例：

```json
{
  "address_id": 1,
  "cart_ids": [10, 11],
  "coupon_id": 3,
  "points_used": 100,
  "buyer_note": "工作日配送"
}
```

说明：

- `coupon_id` 在当前实现中代表 `t_user_coupon.user_coupon_id`，即用户已领取优惠券实例。
- 下单时会记录商品名称、图片、价格、`sku_id`、`sku_text` 快照，避免后续商品变更影响历史订单。
- 普通订单和 SKU 订单下单后增加 `locked_stock`，支付后扣减实际库存。

### 6.2 退货退款

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/orders/{order_id}/refund` | 是 | 用户提交退货申请 |
| GET | `/api/orders/refunds` | 是 | 查询我的退货记录 |

退货申请请求示例：

```json
{
  "reason": "商品有质量问题"
}
```

管理员审核通过后，系统会退回余额、退还抵扣积分、扣回赠送积分、恢复商品或 SKU 库存，并发送个人通知；审核拒绝会恢复订单状态并记录驳回原因。

## 7. 优惠券与评价模块

### 7.1 用户优惠券

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/coupons/available` | 是 | 查询可领取优惠券 |
| GET | `/api/coupons/my` | 是 | 查询我的优惠券 |
| POST | `/api/coupons/{coupon_id}/receive` | 是 | 领取优惠券 |

优惠券支持满减券、折扣券、代金券、最低订单金额、每人领取限制、VIP 专享和有效期校验。

### 7.2 评价

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/reviews/product/{product_id}` | 否 | 查询商品评价 |
| POST | `/api/reviews` | 是 | 创建评价 |
| PUT | `/api/reviews/{review_id}` | 是 | 修改评价 |
| DELETE | `/api/reviews/{review_id}` | 是 | 删除评价 |
| GET | `/api/reviews/my` | 是 | 查询我的评价 |

## 8. 秒杀模块

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/seckill/current` | 否 | 查询当前有效秒杀场次与商品 |
| POST | `/api/seckill/orders` | 是 | 创建秒杀订单 |

秒杀下单请求示例：

```json
{
  "seckill_product_id": 1,
  "sku_id": 25,
  "quantity": 1,
  "address_id": 1
}
```

秒杀规则：

- 场次必须处于开始与结束时间范围内，且状态启用。
- 秒杀商品可以绑定指定 SKU；多规格商品未绑定指定 SKU 时，用户下单必须选择 SKU。
- `seckill_stock` 表示活动池库存，后台添加秒杀商品时会增加商品或 SKU 的 `locked_stock`，避免普通渠道超卖。
- 支持 `limit_per_user` 限购，按用户、商品、SKU 和有效秒杀订单累计校验。

## 9. 消息通知模块

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/notifications` | 是 | 查询系统公告与个人消息 |
| GET | `/api/notifications/unread-count` | 是 | 查询未读数 |
| PUT | `/api/notifications/{notification_id}/read` | 是 | 标记单条已读 |
| POST | `/api/notifications/read-all` | 是 | 全部标记已读 |

通知类型：

| 类型 | 说明 | 已读记录方式 |
|------|------|--------------|
| `1` | 系统公告 | 通过 `t_notification_read` 记录每个用户已读状态 |
| `2` | 个人消息 | 直接更新 `t_notification.is_read` |

## 10. 管理后台模块

### 10.1 用户、订单、统计与商品

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/admin/users` | 管理员 | 用户列表 |
| PUT | `/api/admin/users/{user_id}/status` | 管理员 | 启用或禁用用户 |
| PUT | `/api/admin/users/{user_id}/vip` | 管理员 | 设置用户 VIP |
| GET | `/api/admin/orders` | 管理员 | 订单列表 |
| POST | `/api/admin/orders/{order_id}/ship` | 管理员 | 订单发货 |
| GET | `/api/admin/products` | 管理员 | 商品管理列表 |
| PUT | `/api/admin/products/{product_id}/off-shelf` | 管理员 | 下架商品并处理未完成订单 |
| DELETE | `/api/admin/products/{product_id}/permanent` | 管理员 | 永久删除无订单关联商品 |
| GET | `/api/admin/stats/overview` | 管理员 | 看板总览 |
| GET | `/api/admin/stats/hot-products` | 管理员 | 热销商品排行 |
| GET | `/api/admin/stats/sales-trend` | 管理员 | 销售趋势 |
| GET | `/api/admin/stats/sales-chart` | 管理员 | 销售图表 |
| GET | `/api/admin/stats/product-rank` | 管理员 | 商品排行 |
| GET | `/api/admin/stats/user-growth` | 管理员 | 用户增长 |
| GET | `/api/admin/stats/order-source` | 管理员 | 订单来源 |

### 10.2 优惠券管理

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/admin/coupons` | 管理员 | 查询优惠券 |
| POST | `/api/admin/coupons` | 管理员 | 创建优惠券 |
| PUT | `/api/admin/coupons/{coupon_id}` | 管理员 | 更新优惠券 |
| DELETE | `/api/admin/coupons/{coupon_id}` | 管理员 | 删除优惠券及其领取记录 |

### 10.3 退货、秒杀与通知管理

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/admin/refunds` | 管理员 | 查询退货申请 |
| PUT | `/api/admin/refunds/{refund_id}` | 管理员 | 审核退货申请 |
| GET | `/api/admin/seckill/sessions` | 管理员 | 查询秒杀场次 |
| POST | `/api/admin/seckill/sessions` | 管理员 | 创建秒杀场次 |
| PUT | `/api/admin/seckill/sessions/{session_id}` | 管理员 | 更新秒杀场次 |
| GET | `/api/admin/seckill/products` | 管理员 | 查询秒杀商品 |
| POST | `/api/admin/seckill/products` | 管理员 | 添加秒杀商品并锁定库存 |
| DELETE | `/api/admin/seckill/products/{id}` | 管理员 | 删除秒杀商品并释放剩余锁定库存 |
| GET | `/api/admin/notifications` | 管理员 | 查询通知 |
| POST | `/api/admin/notifications` | 管理员 | 发布系统公告或个人消息 |

## 11. 状态码与业务状态

### 11.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 参数错误或业务校验失败 |
| 401 | 未登录或 Token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 11.2 订单状态

| 值 | 说明 |
|----|------|
| `0` | 待支付 |
| `1` | 已支付 |
| `2` | 已发货 |
| `3` | 已完成 |
| `4` | 已取消 |
| `5` | 已退款 |
| `6` | 退货申请中 |

### 11.3 支付方式

| 值 | 说明 |
|----|------|
| `1` | 支付宝占位 |
| `2` | 微信支付占位 |
| `3` | 银行卡占位 |
| `4` | 积分兑换 |
| `5` | 秒杀订单 |

## 12. 当前限制

- 支付宝、微信、银行卡支付目前是接口占位，实际扣款使用系统余额和积分。
- 短信验证码、第三方登录、地图服务未接入外部服务商。
- `t_operation_log` 已建模，但敏感操作自动落库尚未接入统一中间件。
- 后端缺少系统化单元测试，当前主要依赖前端 lint、构建和 Playwright 冒烟测试。

_最后更新：2026-05-21_
