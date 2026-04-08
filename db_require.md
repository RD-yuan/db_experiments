# 数据库课程设计需求文档

> **重要**：在每次执行任务前，请先阅读此文档！

---

## 1. 项目概述

### 1.1 任务目标
开发一个基于 **B/S 架构** 的 **电子商务平台管理系统**。

### 1.2 技术栈
| 类别 | 选型 |
|------|------|
| 操作系统 | Windows 11 / Linux |
| 开发语言 | **Python 3.10+** |
| 前端技术 | HTML, CSS, JavaScript, **Vue.js** |
| 后端框架 | **Flask** (轻量级Web框架) |
| ORM | **SQLAlchemy** |
| 数据库 | **MySQL 8.0** (InnoDB引擎) |
| 认证方式 | JWT (PyJWT) |
| API文档 | Swagger / Flasgger |
| 版本控制 | Git + GitHub |
| 开发工具 | VS Code |

### 1.3 架构设计
- **前后端分离**的 B/S 架构
- 前端：Vue.js SPA，Element UI，axios 交互
- 后端：Flask + SQLAlchemy (ORM)
- 数据库：MySQL 8.0，第三范式设计

---

## 2. 用户角色

系统面向三类用户：

| 角色 | 描述 |
|------|------|
| **普通用户** | 浏览商品、购物车、下单、支付、评价 |
| **VIP用户** | 普通用户功能 + 专属折扣 + 积分兑换 |
| **管理员** | 用户管理、商品管理、订单管理、营销管理、数据统计 |

---

## 3. 功能模块

### 3.1 普通用户功能
| 模块 | 功能点 |
|------|--------|
| 用户管理 | 注册、登录（密码/验证码/第三方）、个人信息维护、收货地址管理、密码找回 |
| 商品浏览 | 搜索商品、多条件筛选（分类/价格/品牌）、排序（销量/价格/新品）、查看商品详情 |
| 购物车 | 添加商品、修改数量、删除商品、批量结算 |
| 订单管理 | 提交订单、支付（微信/支付宝）、查看订单列表/详情、取消订单、确认收货 |
| 商品评价 | 对已完成订单的商品进行评分、文字评价、上传图片 |
| 消费统计 | 查看个人消费趋势图表、导出消费明细报表 |

### 3.2 VIP用户功能
| 模块 | 功能点 |
|------|--------|
| 专属优惠 | VIP专享折扣价、专属优惠券 |
| 积分体系 | 购物累计积分，积分可兑换商品或优惠券 |
| 优先服务 | 订单优先处理，专属客服通道 |
| 消费分析 | 更详细的消费趋势报表 |

### 3.3 管理员功能
| 模块 | 功能点 |
|------|--------|
| 用户管理 | 查看用户列表、禁用/启用账号、分配VIP等级、查看操作日志 |
| 商品管理 | 商品分类（树形结构）、商品增删改查、上架/下架、批量操作 |
| 订单管理 | 查看所有订单、发货（录入物流单号）、处理退换货申请 |
| 营销管理 | 创建优惠券（满减/折扣/代金券）、定向发放优惠券、查看发放记录 |
| 数据统计 | 实时销售数据、热销商品Top10、地区/年龄消费分析、报表导出 |

---

## 4. 数据库设计（12张核心表）

### 4.1 表清单
| 序号 | 表名 | 描述 |
|------|------|------|
| 1 | `t_user` | 用户表 |
| 2 | `t_product` | 商品表 |
| 3 | `t_category` | 分类表 |
| 4 | `t_order` | 订单表 |
| 5 | `t_order_item` | 订单明细表 |
| 6 | `t_shopping_cart` | 购物车表 |
| 7 | `t_address` | 地址表 |
| 8 | `t_review` | 评价表 |
| 9 | `t_coupon` | 优惠券表 |
| 10 | `t_user_coupon` | 用户优惠券表 |
| 11 | `t_operation_log` | 操作日志表 |
| 12 | `t_points_log` | 积分流水表 |

### 4.2 关键表结构

#### t_user（用户表）
| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| user_id | INT | PRIMARY KEY, AUTO_INCREMENT | 用户唯一标识 |
| username | VARCHAR(50) | NOT NULL | 用户名/昵称 |
| password | VARCHAR(255) | NOT NULL | 加密后的密码（BCrypt） |
| phone | VARCHAR(20) | UNIQUE | 手机号 |
| email | VARCHAR(100) | UNIQUE | 邮箱 |
| avatar | VARCHAR(255) | | 头像URL |
| gender | TINYINT | DEFAULT 0 | 性别：0-未知，1-男，2-女 |
| birthday | DATE | | 生日 |
| is_vip | TINYINT | DEFAULT 0 | 是否VIP：0-否，1-是 |
| vip_expire_time | DATETIME | | VIP到期时间 |
| points | INT | DEFAULT 0 | 积分余额 |
| status | TINYINT | DEFAULT 1 | 状态：0-禁用，1-正常 |
| last_login_time | DATETIME | | 最后登录时间 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 注册时间 |

#### t_product（商品表）
| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| product_id | INT | PRIMARY KEY, AUTO_INCREMENT | 商品唯一标识 |
| name | VARCHAR(200) | NOT NULL | 商品名称 |
| description | TEXT | | 商品描述 |
| price | DECIMAL(10,2) | NOT NULL | 商品价格 |
| original_price | DECIMAL(10,2) | | 原价 |
| vip_price | DECIMAL(10,2) | | VIP专享价 |
| stock | INT | NOT NULL | 库存数量 |
| sold_count | INT | DEFAULT 0 | 累计销量 |
| category_id | INT | FOREIGN KEY | 所属分类ID |
| brand_id | INT | | 所属品牌ID |
| main_image | VARCHAR(255) | | 主图URL |
| status | TINYINT | DEFAULT 1 | 状态：0-下架，1-上架 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### t_order（订单表）
| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| order_id | BIGINT | PRIMARY KEY | 订单号（业务主键） |
| user_id | INT | FOREIGN KEY | 用户ID |
| order_amount | DECIMAL(10,2) | | 订单总金额 |
| discount_amount | DECIMAL(10,2) | | 优惠金额 |
| points_used | INT | | 使用积分 |
| points_discount | DECIMAL(10,2) | | 积分抵扣金额 |
| payment_amount | DECIMAL(10,2) | | 实付金额 |
| status | TINYINT | | 0-待支付，1-已支付，2-已发货，3-已完成，4-已取消 |
| payment_method | TINYINT | | 支付方式 |
| payment_time | DATETIME | | 支付时间 |
| address_snapshot | TEXT | | 地址快照（JSON） |
| create_time | DATETIME | | 创建时间 |

#### t_coupon（优惠券表）
| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| coupon_id | INT | PRIMARY KEY | 主键 |
| name | VARCHAR(100) | | 优惠券名称 |
| type | TINYINT | | 1-满减券，2-折扣券，3-代金券 |
| value | DECIMAL(10,2) | | 优惠值 |
| min_order_amount | DECIMAL(10,2) | | 最低订单金额 |
| start_time | DATETIME | | 生效时间 |
| end_time | DATETIME | | 失效时间 |
| total_quantity | INT | | 发放总数 |
| per_user_limit | INT | | 每人限领数量 |
| is_vip_only | TINYINT | DEFAULT 0 | 是否VIP专属 |

---

## 5. 非功能需求

| 类型 | 具体要求 |
|------|----------|
| **性能** | 支持500用户并发；页面加载≤3秒；搜索响应≤2秒；订单提交≤3秒 |
| **安全** | 密码BCrypt加密；防SQL注入；防XSS；重要操作CSRF防护；HTTPS传输 |
| **可靠性** | 每日全量备份；订单支付事务保证一致性；异常回滚 |
| **易用性** | 界面简洁美观；移动端适配；关键操作有提示 |
| **可扩展性** | 模块化设计，便于后续添加秒杀、直播等功能 |

---

## 6. 开发流程

```
需求分析 → 总体设计 → 详细设计 → 数据库设计 → 编码实现 → 系统测试
```

### 6.1 项目目录结构（建议）
```
db_experiments/
├── db_require.md          # 需求文档（本文件）
├── docs/                   # 设计文档
│   ├── database_design.md  # 数据库设计文档
│   └── api_design.md       # API接口设计
├── backend/                # Flask后端
│   ├── app/
│   │   ├── __init__.py     # Flask应用工厂
│   │   ├── config.py       # 配置文件
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # 路由/视图
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── migrations/         # 数据库迁移
│   ├── requirements.txt
│   └── run.py
├── frontend/               # Vue.js前端
│   ├── src/
│   ├── public/
│   └── package.json
└── sql/                    # SQL脚本
    ├── schema.sql          # 表结构
    └── init_data.sql       # 初始数据
```

---

## 7. 执行 Prompt（自执行指南）

当开始任何开发任务时，请遵循以下流程：

### Step 1: 确认需求
> 先阅读本需求文档（db_require.md），理解当前任务属于哪个模块。

### Step 2: 数据库优先
> 先完成数据库设计和SQL脚本，再进行后端开发。

### Step 3: 后端先行
> 先完成后端API，确保功能可用，再进行前端开发。

### Step 4: 模块化开发
> 按功能模块逐步开发：用户 → 商品 → 购物车 → 订单 → 优惠券 → 统计

### Step 5: 测试验证
> 每完成一个模块，编写测试用例进行验证。

---

## 8. 当前项目状态

| 模块 | 状态 | 备注 |
|------|------|------|
| 项目初始化 | ✅ 完成 | 目录结构已创建 |
| 需求分析 | ✅ 完成 | 本文档 |
| 数据库设计 | ✅ 完成 | schema.sql, init_data.sql |
| 后端开发 | ⏳ 待开始 | - |
| 前端开发 | ⏳ 待开始 | - |
| 系统测试 | ⏳ 待开始 | - |

---

## 9. 注意事项

1. **不要直接给出完整代码**，优先引导思考
2. **分模块完成**，每完成一个模块进行测试
3. **遵循Django最佳实践**，使用ORM而非原生SQL
4. **注意安全性**：密码加密、防注入、防XSS
5. **事务管理**：订单创建、库存扣减等操作需保证原子性

---

_最后更新：2026-04-08_
