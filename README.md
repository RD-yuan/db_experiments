# 🛒 电子商务平台管理系统

> 北京邮电大学 - 数据库系统原理课程设计

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-orange.svg)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue-3.3-brightgreen.svg)](https://vuejs.org/)

一个基于 **Flask + Vue3 + MySQL** 的全栈电子商务平台，支持用户购物、订单管理、数据可视化等功能。

---

## 📖 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [功能演示](#功能演示)
- [API文档](#api文档)
- [数据库设计](#数据库设计)
- [部署说明](#部署说明)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

### 背景

本项目是北京邮电大学数据库系统原理课程设计作业，旨在开发一个功能完善的电子商务平台管理系统。

### 目标

- 实现完整的电商购物流程
- 提供用户友好的界面和交互体验
- 支持数据可视化和报表导出
- 采用前后端分离架构，便于维护和扩展

---

## 功能特性

### 👤 用户功能

#### 🛍️ 商品浏览
- ✅ 关键词搜索商品
- ✅ 多条件筛选（分类/价格/品牌）
- ✅ 多维度排序（价格/销量/新品）
- ✅ 商品详情查看
- ✅ 用户评价浏览

#### 🛒 购物车
- ✅ 添加商品到购物车
- ✅ 修改商品数量
- ✅ 批量选择商品
- ✅ 删除购物车商品
- ✅ 实时价格计算

#### 📦 订单管理
- ✅ 创建订单
- ✅ 订单支付（模拟）
- ✅ 查看订单列表
- ✅ 订单详情查看
- ✅ 取消订单
- ✅ 确认收货

#### ⭐ 评价系统
- ✅ 订单评价（评分/评论/图片）
- ✅ 查看我的评价

#### 🎫 优惠券
- ✅ 领取优惠券
- ✅ 查看我的优惠券
- ✅ 订单使用优惠券

#### 📊 消费统计
- ✅ **消费趋势可视化**（柱状图/折线图）
- ✅ **商品分类占比分析**（饼图）
- ✅ 按日/周/月查看
- ✅ 自定义时间范围
- ✅ **导出Excel报表**

### 👨‍💼 管理员功能

#### 👥 用户管理
- ✅ 用户列表查看
- ✅ 用户状态管理（启用/禁用）
- ✅ VIP等级设置

#### 📦 商品管理
- ✅ 商品CRUD操作
- ✅ 商品上下架
- ✅ 多级分类管理

#### 📋 订单管理
- ✅ 订单列表查看
- ✅ 订单发货
- ✅ 退换货处理

#### 📈 数据统计
- ✅ **数据看板**（ECharts可视化）
- ✅ 销售趋势图
- ✅ 热销商品Top10
- ✅ 用户消费分析

#### 🎫 优惠券管理
- ✅ 创建优惠券
- ✅ 发放优惠券

---

## 技术栈

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.10+ | 编程语言 |
| **Flask** | 3.0 | Web框架 |
| **SQLAlchemy** | 2.0 | ORM框架 |
| **Flask-Migrate** | 4.0 | 数据库迁移 |
| **PyJWT** | 2.8 | JWT认证 |
| **bcrypt** | 4.1 | 密码加密 |
| **Flasgger** | 0.9 | API文档 |
| **PyMySQL** | 1.1 | MySQL驱动 |

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue** | 3.3 | 前端框架 |
| **Vue Router** | 4.2 | 路由管理 |
| **Pinia** | 2.1 | 状态管理 |
| **Element Plus** | 2.4 | UI组件库 |
| **ECharts** | 5.4 | 数据可视化 |
| **Axios** | 1.6 | HTTP客户端 |
| **dayjs** | 1.11 | 日期处理 |
| **xlsx** | 0.18 | Excel导出 |

### 数据库

| 技术 | 版本 | 说明 |
|------|------|------|
| **MySQL** | 8.0 | 关系型数据库 |
| **InnoDB** | - | 存储引擎 |

---

## 项目结构

```
db_experiments/
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── __init__.py      # Flask应用工厂
│   │   ├── config.py        # 配置文件
│   │   ├── models/          # 数据模型
│   │   │   └── models.py    # 12张表的模型
│   │   ├── routes/          # 路由模块
│   │   │   ├── auth.py      # 认证
│   │   │   ├── user.py      # 用户
│   │   │   ├── product.py   # 商品
│   │   │   ├── category.py  # 分类
│   │   │   ├── cart.py      # 购物车
│   │   │   ├── order.py     # 订单
│   │   │   ├── coupon.py    # 优惠券
│   │   │   ├── review.py    # 评价
│   │   │   └── admin.py     # 管理员
│   │   └── utils/           # 工具函数
│   │       └── helpers.py   # JWT/加密/分页
│   ├── migrations/          # 数据库迁移
│   ├── requirements.txt     # 依赖列表
│   ├── run.py              # 启动文件
│   └── README.md           # 后端文档
│
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── main.js         # Vue入口
│   │   ├── App.vue         # 根组件
│   │   ├── router/         # 路由配置
│   │   ├── api/            # API封装
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件
│   │   │   ├── auth/       # 登录注册
│   │   │   ├── product/    # 商品页面
│   │   │   ├── cart/       # 购物车
│   │   │   ├── order/      # 订单页面
│   │   │   ├── user/       # 用户中心
│   │   │   ├── admin/      # 管理员后台
│   │   │   └── layout/     # 布局组件
│   │   └── assets/         # 静态资源
│   ├── package.json        # 依赖配置
│   └── README.md           # 前端文档
│
├── sql/                     # 数据库脚本
│   ├── schema.sql          # 表结构
│   └── init_data.sql       # 初始数据
│
├── docs/                    # 文档
│   ├── database_design.md   # 数据库设计文档
│   ├── api_design.md        # API设计文档
│   └── 需求对比分析.md      # 需求对比
│
├── BRANCH_STRATEGY.md       # Git分支策略
├── CHAT_HISTORY.md          # 开发记录
├── db_require.md            # 需求文档
└── README.md                # 本文件
```

---

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone https://github.com/RD-yuan/db_experiments.git
cd db_experiments
```

### 2. 配置数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入表结构和初始数据
USE ecommerce_db;
SOURCE sql/schema.sql;
SOURCE sql/init_data.sql;
```

### 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（必须！）
cp .env.example .env
# 编辑 .env 文件，修改数据库连接信息为你本地的 MySQL 配置
# 必须修改: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, SECRET_KEY, JWT_SECRET_KEY

# 启动服务
python run.py
```

后端将在 http://localhost:5000 启动

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

前端将在 http://localhost:5173 启动

### 5. 访问系统

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/apidocs

### 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 用户 | testuser | 123456 |

---

## 功能演示

### 用户端

#### 1. 商品浏览
![商品列表](./screenshots/products.png)
- 搜索、筛选、排序功能
- 分页展示

#### 2. 商品详情
![商品详情](./screenshots/product-detail.png)
- 商品信息展示
- 用户评价

#### 3. 购物车
![购物车](./screenshots/cart.png)
- 数量修改
- 批量选择

#### 4. 订单管理
![订单列表](./screenshots/orders.png)
- 状态筛选
- 订单操作

#### 5. 消费统计
![消费统计](./screenshots/stats.png)
- ECharts可视化
- Excel导出

### 管理员端

#### 1. 数据看板
![数据看板](./screenshots/dashboard.png)
- 销售趋势
- 热销商品

#### 2. 用户管理
![用户管理](./screenshots/users.png)
- 用户列表
- 权限管理

---

## API文档

### 认证相关

#### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "password": "123456",
  "phone": "13800138000",
  "email": "test@example.com"
}
```

#### 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "123456"
}
```

### 商品相关

#### 商品列表
```http
GET /api/products?page=1&per_page=20&keyword=iPhone&category_id=1&sort=price&order=desc
Authorization: Bearer <token>
```

#### 商品详情
```http
GET /api/products/1
```

### 订单相关

#### 创建订单
```http
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "address_id": 1,
  "cart_ids": [1, 2, 3],
  "coupon_id": 1,
  "points_used": 100,
  "buyer_note": "请尽快发货"
}
```

### 消费统计

#### 获取消费统计
```http
GET /api/users/consumption-stats?start_date=2024-01-01&end_date=2024-12-31&period=daily
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_stats": {
      "total_orders": 50,
      "total_amount": 12580.50
    },
    "trend": [
      {
        "date": "2024-01-01",
        "order_count": 3,
        "amount": 580.00
      }
    ],
    "category_distribution": [
      {
        "name": "电子产品",
        "value": 8500.00
      }
    ]
  }
}
```

📖 **完整API文档**: 访问 http://localhost:5000/apidocs

---

## 数据库设计

### ER图

```
┌─────────┐       ┌──────────┐       ┌──────────┐
│  User   │       │ Product  │       │ Category │
└────┬────┘       └────┬─────┘       └────┬─────┘
     │                 │                  │
     │                 │                  │
     ▼                 ▼                  │
┌─────────┐       ┌──────────┐           │
│ Address │       │   Cart   │           │
└─────────┘       └──────────┘           │
     │                 │                  │
     │                 │                  │
     └────────┐        │                  │
              ▼        │                  │
          ┌────────┐   │                  │
          │ Order  │◄──┘                  │
          └───┬────┘                      │
              │                           │
              ▼                           │
        ┌──────────┐                      │
        │OrderItem │◄─────────────────────┘
        └──────────┘
```

### 核心表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| t_user | 用户表 | user_id, username, is_vip, points |
| t_product | 商品表 | product_id, name, price, stock, locked_stock |
| t_category | 分类表 | category_id, name, parent_id |
| t_order | 订单表 | order_id, user_id, payment_amount, status |
| t_order_item | 订单明细 | order_item_id, product_id, quantity |
| t_shopping_cart | 购物车 | cart_id, user_id, product_id, quantity |
| t_coupon | 优惠券 | coupon_id, type, value, min_order_amount |
| t_user_coupon | 用户优惠券 | user_coupon_id, user_id, coupon_id, status |
| t_address | 地址表 | address_id, user_id, recipient_name |
| t_review | 评价表 | review_id, user_id, product_id, rating |
| t_points_log | 积分流水 | log_id, user_id, type, amount |
| t_operation_log | 操作日志 | log_id, user_id, operation_type |

### 设计亮点

1. **库存管理**: 双字段设计（stock + locked_stock）防止超卖
2. **订单快照**: 保存商品和地址快照，保证历史数据准确
3. **树形分类**: parent_id 实现多级分类
4. **VIP体系**: 支持VIP等级和专属价格
5. **积分系统**: 完整的积分流水记录

📖 **详细设计文档**: [docs/database_design.md](docs/database_design.md)

---

## 部署说明

### Docker部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 手动部署

#### 后端部署

```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### 前端部署

```bash
# 构建生产版本
npm run build

# 使用 Nginx 托管
cp -r dist/* /var/www/html/
```

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 开发指南

### Git分支策略

```
main (生产环境)
  ↑
  └── dev (开发集成分支)
        ├── backend (后端开发)
        └── frontend (前端开发)
```

### 开发流程

1. **切换到对应分支**
```bash
# 后端开发
git checkout backend

# 前端开发
git checkout frontend
```

2. **开发功能**
```bash
# 编写代码...
git add .
git commit -m "feat: 添加XXX功能"
git push
```

3. **合并到dev分支**
```bash
git checkout dev
git merge backend  # 或 frontend
git push
```

4. **测试通过后发布**
```bash
git checkout main
git merge dev
git push
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/):

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat: 添加用户登录功能 |
| fix | 修复bug | fix: 修复订单库存扣减bug |
| docs | 文档更新 | docs: 更新API文档 |
| style | 代码格式 | style: 格式化代码 |
| refactor | 重构 | refactor: 重构用户模块 |
| test | 测试 | test: 添加单元测试 |

---

## 常见问题

### 1. 数据库连接失败
**问题**: `Can't connect to MySQL server`

**解决方案**:
- 检查MySQL服务是否启动
- 确认 `.env` 文件中的数据库配置正确
- 检查数据库用户权限

### 2. 前端无法访问后端API
**问题**: `CORS policy error`

**解决方案**:
- 后端已配置CORS，确保后端服务正常运行
- 检查API地址配置是否正确

### 3. JWT Token过期
**问题**: `Token expired`

**解决方案**:
- 重新登录获取新Token
- 前端会自动跳转到登录页

### 4. 图片上传失败
**问题**: `File too large`

**解决方案**:
- 检查文件大小（默认限制16MB）
- 检查文件格式（支持 png/jpg/jpeg/gif）

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范

- Python: 遵循 PEP 8
- JavaScript: 遵循 ESLint 配置
- 提交信息: 遵循 Conventional Commits

---

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 联系方式

- **作者**: 黄浩洵、赵岳、王馨凝、马诺西
- **学校**: 北京邮电大学
- **课程**: 数据库系统原理
- **时间**: 2026年3月

---

## 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)

---

⭐ 如果这个项目对你有帮助，请给一个 Star！⭐
