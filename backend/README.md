# 电子商务平台后端 API

基于 Flask + SQLAlchemy + MySQL 的电子商务平台后端服务。

## 技术栈

- **Flask 3.0** - Web 框架
- **SQLAlchemy** - ORM
- **Flask-Migrate** - 数据库迁移
- **Flask-RESTful** - REST API
- **Flasgger** - Swagger API 文档
- **PyJWT** - JWT 认证
- **MySQL 8.0** - 数据库

## 项目结构

```
backend/
├── app/
│   ├── __init__.py         # Flask 应用工厂
│   ├── config.py           # 配置文件
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py       # 数据模型
│   ├── routes/
│   │   ├── auth.py         # 认证路由 (注册/登录)
│   │   ├── user.py         # 用户路由
│   │   ├── product.py      # 商品路由
│   │   ├── category.py     # 分类路由
│   │   ├── cart.py         # 购物车路由
│   │   ├── order.py        # 订单路由
│   │   ├── coupon.py       # 优惠券路由
│   │   ├── review.py       # 评价路由
│   │   └── admin.py        # 管理员路由
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # 工具函数
├── migrations/             # 数据库迁移文件
├── .env.example           # 环境变量示例
├── requirements.txt       # 依赖
└── run.py                 # 启动文件
```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

> ⚠️ **必须操作**：将 `.env.example` 复制为 `.env`，并修改其中的数据库配置为你本地的 MySQL 连接信息。

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，**至少修改以下项**：

```ini
MYSQL_HOST=localhost      # MySQL 地址
MYSQL_USER=root           # MySQL 用户名
MYSQL_PASSWORD=你的密码    # MySQL 密码
MYSQL_DATABASE=ecommerce_db
SECRET_KEY=随机字符串      # 生产环境务必修改
JWT_SECRET_KEY=随机字符串   # 生产环境务必修改
```

### 4. 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 导入数据库结构

```bash
mysql -u root -p ecommerce_db < ../sql/schema.sql
mysql -u root -p ecommerce_db < ../sql/init_data.sql
```

### 6. 启动服务

```bash
python run.py
```

服务将在 http://localhost:5000 启动

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:5000/apidocs
- Health Check: http://localhost:5000/health

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

### 用户
- `GET /api/users/profile` - 获取用户信息
- `PUT /api/users/profile` - 更新用户信息
- `GET /api/users/addresses` - 获取地址列表
- `POST /api/users/addresses` - 添加地址
- `PUT /api/users/addresses/<id>` - 更新地址
- `DELETE /api/users/addresses/<id>` - 删除地址

### 商品
- `GET /api/products` - 获取商品列表
- `GET /api/products/<id>` - 获取商品详情
- `GET /api/products/hot` - 获取热销商品
- `GET /api/products/new` - 获取新品

### 分类
- `GET /api/categories` - 获取分类列表（树形）
- `GET /api/categories/<id>` - 获取分类详情

### 购物车
- `GET /api/cart` - 获取购物车
- `POST /api/cart` - 添加商品到购物车
- `PUT /api/cart/<id>` - 更新购物车项
- `DELETE /api/cart/<id>` - 删除购物车项
- `POST /api/cart/clear` - 清空购物车

### 订单
- `GET /api/orders` - 获取订单列表
- `GET /api/orders/<id>` - 获取订单详情
- `POST /api/orders` - 创建订单
- `POST /api/orders/<id>/pay` - 支付订单
- `POST /api/orders/<id>/cancel` - 取消订单
- `POST /api/orders/<id>/receive` - 确认收货

### 优惠券
- `GET /api/coupons/available` - 获取可领取优惠券
- `GET /api/coupons/my` - 获取我的优惠券
- `POST /api/coupons/<id>/receive` - 领取优惠券

### 评价
- `GET /api/reviews/product/<id>` - 获取商品评价
- `POST /api/reviews` - 提交评价
- `GET /api/reviews/my` - 获取我的评价

### 管理员
- `GET /api/admin/users` - 获取用户列表
- `PUT /api/admin/users/<id>/status` - 启用/禁用用户
- `PUT /api/admin/users/<id>/vip` - 设置用户VIP
- `GET /api/admin/orders` - 获取所有订单
- `POST /api/admin/orders/<id>/ship` - 发货
- `GET /api/admin/stats/overview` - 数据概览
- `GET /api/admin/stats/hot-products` - 热销商品
- `GET /api/admin/stats/sales-trend` - 销售趋势

## 测试账号

| 用户 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 管理员 |
| testuser | 123456 | 普通用户 |

## 开发指南

### 数据库迁移

```bash
# 初始化迁移
flask db init

# 生成迁移脚本
flask db migrate -m "描述"

# 执行迁移
flask db upgrade
```

### 运行测试

```bash
pytest
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_ENV | 运行环境 | development |
| SECRET_KEY | Flask 密钥 | - |
| JWT_SECRET_KEY | JWT 密钥 | - |
| MYSQL_HOST | MySQL 主机 | localhost |
| MYSQL_PORT | MySQL 端口 | 3306 |
| MYSQL_USER | MySQL 用户 | root |
| MYSQL_PASSWORD | MySQL 密码 | - |
| MYSQL_DATABASE | 数据库名 | ecommerce_db |

## License

MIT
