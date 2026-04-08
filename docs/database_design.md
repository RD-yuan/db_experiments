# 数据库设计文档

## 1. 数据库概述

### 1.1 基本信息
| 项目 | 配置 |
|------|------|
| 数据库名 | `ecommerce_db` |
| 字符集 | `utf8mb4` |
| 排序规则 | `utf8mb4_unicode_ci` |
| 存储引擎 | `InnoDB` |
| MySQL版本 | `8.0+` |

### 1.2 设计原则
- 遵循 **第三范式 (3NF)**，消除数据冗余
- 合理设置 **索引**，优化查询性能
- 使用 **外键约束**，保证数据完整性
- 采用 **逻辑删除**，保留历史数据
- **快照机制**：订单保存商品信息快照，防止商品信息变更影响历史订单

---

## 2. 表结构设计

### 2.1 表清单

| 序号 | 表名 | 中文名 | 记录数估算 |
|------|------|--------|------------|
| 1 | t_user | 用户表 | 10万+ |
| 2 | t_category | 分类表 | 100+ |
| 3 | t_product | 商品表 | 1万+ |
| 4 | t_address | 地址表 | 20万+ |
| 5 | t_shopping_cart | 购物车表 | 50万+ |
| 6 | t_coupon | 优惠券表 | 100+ |
| 7 | t_user_coupon | 用户优惠券表 | 100万+ |
| 8 | t_order | 订单表 | 500万+ |
| 9 | t_order_item | 订单明细表 | 1500万+ |
| 10 | t_review | 评价表 | 300万+ |
| 11 | t_points_log | 积分流水表 | 1000万+ |
| 12 | t_operation_log | 操作日志表 | 5000万+ |

### 2.2 ER关系图

```
                    ┌─────────────┐
                    │   t_user    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┬──────────────────┐
        │                  │                  │                  │
        ▼                  ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  t_address    │  │t_shopping_cart│  │   t_order     │  │ t_user_coupon │
└───────────────┘  └───────────────┘  └───────┬───────┘  └───────┬───────┘
                                              │                  │
                                              ▼                  │
                                      ┌───────────────┐          │
                                      │t_order_item   │          │
                                      └───────┬───────┘          │
                                              │                  │
                        ┌─────────────────────┼──────────────────┘
                        │                     │
                        ▼                     ▼
                ┌───────────────┐      ┌───────────────┐
                │  t_product    │◄─────│   t_review    │
                └───────┬───────┘      └───────────────┘
                        │
                        ▼
                ┌───────────────┐
                │  t_category   │
                └───────────────┘

        ┌───────────────┐              ┌───────────────┐
        │   t_coupon    │──────────────│ t_user_coupon │
        └───────────────┘              └───────────────┘
```

---

## 3. 核心表详细设计

### 3.1 用户表 (t_user)

**用途**：存储所有用户信息，包括普通用户、VIP用户、管理员。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | NOT NULL | 用户名 |
| password | VARCHAR(255) | NOT NULL | 密码(BCrypt) |
| phone | VARCHAR(20) | UNIQUE | 手机号 |
| email | VARCHAR(100) | UNIQUE | 邮箱 |
| avatar | VARCHAR(255) | | 头像URL |
| gender | TINYINT | DEFAULT 0 | 0-未知 1-男 2-女 |
| birthday | DATE | | 生日 |
| is_vip | TINYINT | DEFAULT 0 | 是否VIP |
| vip_level | TINYINT | DEFAULT 0 | VIP等级 |
| vip_expire_time | DATETIME | | VIP到期时间 |
| points | INT | DEFAULT 0 | 积分余额 |
| status | TINYINT | DEFAULT 1 | 0-禁用 1-正常 |
| last_login_time | DATETIME | | 最后登录时间 |
| last_login_ip | VARCHAR(50) | | 最后登录IP |
| create_time | DATETIME | DEFAULT CURRENT | 创建时间 |
| update_time | DATETIME | ON UPDATE | 更新时间 |

**索引设计**：
- `idx_phone` - 手机号查询（登录）
- `idx_email` - 邮箱查询（登录）
- `idx_status` - 状态筛选
- `idx_create_time` - 注册时间排序

---

### 3.2 商品表 (t_product)

**用途**：存储商品基本信息、价格、库存等。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| product_id | INT | PK, AUTO_INCREMENT | 商品ID |
| name | VARCHAR(200) | NOT NULL | 商品名称 |
| description | TEXT | | 商品描述 |
| price | DECIMAL(10,2) | NOT NULL | 销售价 |
| original_price | DECIMAL(10,2) | | 原价（划线价） |
| vip_price | DECIMAL(10,2) | | VIP专享价 |
| stock | INT | NOT NULL | 库存数量 |
| locked_stock | INT | DEFAULT 0 | 锁定库存 |
| sold_count | INT | DEFAULT 0 | 累计销量 |
| category_id | INT | FK | 分类ID |
| brand | VARCHAR(100) | | 品牌 |
| main_image | VARCHAR(255) | | 主图URL |
| sub_images | TEXT | | 副图JSON数组 |
| status | TINYINT | DEFAULT 1 | 0-下架 1-上架 |
| is_hot | TINYINT | DEFAULT 0 | 是否热销 |
| is_new | TINYINT | DEFAULT 0 | 是否新品 |
| is_recommend | TINYINT | DEFAULT 0 | 是否推荐 |

**库存管理设计**：
- `stock`：实际可用库存
- `locked_stock`：下单时锁定，支付成功扣减，取消订单释放
- 实际可售库存 = `stock` - `locked_stock`

---

### 3.3 订单表 (t_order)

**用途**：存储订单主信息，包括金额、状态、物流等。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| order_id | BIGINT | PK | 订单号（业务生成） |
| user_id | INT | FK, NOT NULL | 用户ID |
| total_amount | DECIMAL(10,2) | NOT NULL | 商品总金额 |
| freight_amount | DECIMAL(10,2) | DEFAULT 0 | 运费 |
| discount_amount | DECIMAL(10,2) | DEFAULT 0 | 优惠券优惠 |
| points_used | INT | DEFAULT 0 | 使用积分 |
| points_discount | DECIMAL(10,2) | DEFAULT 0 | 积分抵扣金额 |
| payment_amount | DECIMAL(10,2) | NOT NULL | 实付金额 |
| status | TINYINT | DEFAULT 0 | 订单状态 |
| payment_method | TINYINT | | 1-微信 2-支付宝 3-余额 |
| payment_time | DATETIME | | 支付时间 |
| transaction_id | VARCHAR(100) | | 第三方交易号 |
| shipping_company | VARCHAR(50) | | 物流公司 |
| shipping_number | VARCHAR(100) | | 物流单号 |
| shipping_time | DATETIME | | 发货时间 |
| receive_time | DATETIME | | 收货时间 |
| address_snapshot | TEXT | | 地址快照JSON |

**订单状态流转**：
```
待支付(0) ──支付成功──► 已支付(1) ──发货──► 已发货(2) ──确认收货──► 已完成(3)
    │                      │                │
    └───超时取消───► 已取消(4)                 │
                          └─────退款────► 已退款(5)
```

---

### 3.4 优惠券表 (t_coupon)

**用途**：存储优惠券模板信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| coupon_id | INT | PK | 优惠券ID |
| name | VARCHAR(100) | NOT NULL | 名称 |
| type | TINYINT | NOT NULL | 1-满减 2-折扣 3-代金 |
| value | DECIMAL(10,2) | NOT NULL | 优惠值 |
| min_order_amount | DECIMAL(10,2) | DEFAULT 0 | 最低订单金额 |
| max_discount | DECIMAL(10,2) | | 最大优惠(折扣券) |
| start_time | DATETIME | NOT NULL | 生效时间 |
| end_time | DATETIME | NOT NULL | 失效时间 |
| total_quantity | INT | | 发放总数 |
| received_count | INT | DEFAULT 0 | 已领取数 |
| per_user_limit | INT | DEFAULT 1 | 每人限领 |
| is_vip_only | TINYINT | DEFAULT 0 | 是否VIP专属 |

**优惠券类型说明**：
- **满减券(type=1)**：满X元减Y元，`value`为减免金额
- **折扣券(type=2)**：X折优惠，`value`为折扣率（如0.9表示9折）
- **代金券(type=3)**：无门槛抵扣，`value`为抵扣金额

---

## 4. 索引设计原则

### 4.1 索引类型
| 类型 | 使用场景 | 示例 |
|------|----------|------|
| 主键索引 | 唯一标识 | user_id, order_id |
| 唯一索引 | 唯一约束 | phone, email |
| 普通索引 | 频繁查询 | status, create_time |
| 组合索引 | 多条件查询 | (user_id, status) |
| 外键索引 | 关联查询 | category_id |

### 4.2 索引优化建议
1. **WHERE条件字段**建立索引
2. **ORDER BY排序字段**建立索引
3. **JOIN关联字段**建立索引
4. 避免**过多索引**，影响写入性能
5. **组合索引**遵循最左前缀原则

---

## 5. 事务设计

### 5.1 订单创建事务

```sql
START TRANSACTION;

-- 1. 锁定库存
SELECT stock, locked_stock FROM t_product 
WHERE product_id = ? FOR UPDATE;

-- 2. 检查库存是否充足
-- 3. 更新锁定库存
UPDATE t_product 
SET locked_stock = locked_stock + ? 
WHERE product_id = ?;

-- 4. 创建订单
INSERT INTO t_order (...) VALUES (...);

-- 5. 创建订单明细
INSERT INTO t_order_item (...) VALUES (...);

-- 6. 清空购物车
DELETE FROM t_shopping_cart 
WHERE user_id = ? AND selected = 1;

COMMIT;
-- 异常时 ROLLBACK;
```

### 5.2 支付成功事务

```sql
START TRANSACTION;

-- 1. 更新订单状态
UPDATE t_order 
SET status = 1, payment_time = NOW() 
WHERE order_id = ?;

-- 2. 扣减库存
UPDATE t_product 
SET stock = stock - ?, locked_stock = locked_stock - ?, sold_count = sold_count + ?
WHERE product_id = ?;

-- 3. 使用优惠券
UPDATE t_user_coupon 
SET status = 1, use_time = NOW(), order_id = ?
WHERE user_coupon_id = ?;

-- 4. 扣减积分
UPDATE t_user SET points = points - ? WHERE user_id = ?;

-- 5. 记录积分流水
INSERT INTO t_points_log (...) VALUES (...);

COMMIT;
```

---

## 6. 数据安全

### 6.1 密码安全
- 使用 **BCrypt** 算法加密
- 自动加盐，防止彩虹表攻击
- 不存储明文密码

### 6.2 敏感数据处理
- 身份证、银行卡等**加密存储**
- 日志中**脱敏处理**
- 地址快照使用**JSON格式**

### 6.3 软删除设计
- 使用 `status` 字段标记删除状态
- 不使用物理删除，保留历史数据

---

## 7. 性能优化

### 7.1 分页查询优化
```sql
-- 避免 OFFSET 过大
SELECT * FROM t_order 
WHERE user_id = ? AND create_time > ?
ORDER BY create_time DESC 
LIMIT 20;
```

### 7.2 读写分离建议
- 主库：写操作
- 从库：读操作、报表统计

### 7.3 缓存策略
| 数据 | 缓存时间 | 缓存位置 |
|------|----------|----------|
| 商品信息 | 5分钟 | Redis |
| 分类数据 | 1小时 | Redis |
| 用户Session | 30分钟 | Redis |
| 热销商品 | 10分钟 | Redis |

---

## 8. 执行脚本

### 8.1 建表
```bash
mysql -u root -p < sql/schema.sql
```

### 8.2 初始化数据
```bash
mysql -u root -p < sql/init_data.sql
```

---

_文档版本: 1.0_  
_最后更新: 2026-04-08_
