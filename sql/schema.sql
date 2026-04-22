-- ============================================================
-- 电子商务平台数据库设计
-- 数据库: MySQL 8.0
-- 字符集: utf8mb4
-- 创建时间: 2026-04-08
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_db
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce_db;

-- ============================================================
-- 1. 用户表 (t_user)
-- ============================================================
DROP TABLE IF EXISTS t_user;
CREATE TABLE t_user (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(BCrypt加密)',
    phone VARCHAR(20) UNIQUE COMMENT '手机号',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    avatar VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    gender TINYINT DEFAULT 0 COMMENT '性别: 0-未知 1-男 2-女',
    birthday DATE DEFAULT NULL COMMENT '生日',
    is_vip TINYINT DEFAULT 0 COMMENT '是否VIP: 0-否 1-是',
    vip_level TINYINT DEFAULT 0 COMMENT 'VIP等级: 0-普通 1-银卡 2-金卡 3-钻石',
    vip_expire_time DATETIME DEFAULT NULL COMMENT 'VIP到期时间',
    points INT DEFAULT 0 COMMENT '积分余额',
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用 1-正常',
    last_login_time DATETIME DEFAULT NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_admin TINYINT DEFAULT 0 COMMENT '是否管理员: 0-否 1-是',
    
    INDEX idx_phone (phone),
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_is_admin (is_admin),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. 分类表 (t_category) - 树形结构
-- ============================================================
DROP TABLE IF EXISTS t_category;
CREATE TABLE t_category (
    category_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '分类ID',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    parent_id INT DEFAULT 0 COMMENT '父分类ID: 0表示一级分类',
    level TINYINT DEFAULT 1 COMMENT '层级: 1-一级 2-二级 3-三级',
    icon VARCHAR(255) DEFAULT NULL COMMENT '分类图标',
    sort_order INT DEFAULT 0 COMMENT '排序(越小越靠前)',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用 1-正常',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status),
    INDEX idx_sort_order (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- ============================================================
-- 3. 商品表 (t_product)
-- ============================================================
DROP TABLE IF EXISTS t_product;
CREATE TABLE t_product (
    product_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品ID',
    name VARCHAR(200) NOT NULL COMMENT '商品名称',
    description TEXT COMMENT '商品描述',
    price DECIMAL(10,2) NOT NULL COMMENT '销售价',
    original_price DECIMAL(10,2) DEFAULT NULL COMMENT '原价',
    vip_price DECIMAL(10,2) DEFAULT NULL COMMENT 'VIP专享价',
    exchange_points INT NOT NULL DEFAULT 0 COMMENT '积分兑换所需积分，0表示不可兑换',
    stock INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    locked_stock INT DEFAULT 0 COMMENT '锁定库存(下单未支付)',
    sold_count INT DEFAULT 0 COMMENT '累计销量',
    category_id INT DEFAULT NULL COMMENT '分类ID',
    brand VARCHAR(100) DEFAULT NULL COMMENT '品牌',
    main_image VARCHAR(255) DEFAULT NULL COMMENT '主图URL',
    sub_images TEXT COMMENT '副图URL(JSON数组)',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-下架 1-上架',
    is_hot TINYINT DEFAULT 0 COMMENT '是否热销: 0-否 1-是',
    is_new TINYINT DEFAULT 0 COMMENT '是否新品: 0-否 1-是',
    is_recommend TINYINT DEFAULT 0 COMMENT '是否推荐: 0-否 1-是',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_price (price),
    INDEX idx_sold_count (sold_count),
    INDEX idx_create_time (create_time),
    INDEX idx_is_hot (is_hot),
    INDEX idx_is_new (is_new),
    INDEX idx_exchange_points (exchange_points),
    
    FOREIGN KEY (category_id) REFERENCES t_category(category_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- ============================================================
-- 4. 地址表 (t_address)
-- ============================================================
DROP TABLE IF EXISTS t_address;
CREATE TABLE t_address (
    address_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '地址ID',
    user_id INT NOT NULL COMMENT '用户ID',
    recipient_name VARCHAR(50) NOT NULL COMMENT '收货人姓名',
    recipient_phone VARCHAR(20) NOT NULL COMMENT '收货人电话',
    province VARCHAR(50) NOT NULL COMMENT '省份',
    city VARCHAR(50) NOT NULL COMMENT '城市',
    district VARCHAR(50) DEFAULT NULL COMMENT '区/县',
    detail_address VARCHAR(255) NOT NULL COMMENT '详细地址',
    postal_code VARCHAR(20) DEFAULT NULL COMMENT '邮政编码',
    is_default TINYINT DEFAULT 0 COMMENT '是否默认: 0-否 1-是',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_is_default (is_default),
    
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收货地址表';

-- ============================================================
-- 5. 购物车表 (t_shopping_cart)
-- ============================================================
DROP TABLE IF EXISTS t_shopping_cart;
CREATE TABLE t_shopping_cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '购物车ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
    selected TINYINT DEFAULT 1 COMMENT '是否选中: 0-否 1-是',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_user_product (user_id, product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES t_product(product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='购物车表';

-- ============================================================
-- 6. 优惠券表 (t_coupon)
-- ============================================================
DROP TABLE IF EXISTS t_coupon;
CREATE TABLE t_coupon (
    coupon_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '优惠券ID',
    name VARCHAR(100) NOT NULL COMMENT '优惠券名称',
    type TINYINT NOT NULL COMMENT '类型: 1-满减券 2-折扣券 3-代金券',
    value DECIMAL(10,2) NOT NULL COMMENT '优惠值(满减/代金为金额,折扣为折扣率如0.9)',
    min_order_amount DECIMAL(10,2) DEFAULT 0 COMMENT '最低订单金额',
    max_discount DECIMAL(10,2) DEFAULT NULL COMMENT '最大优惠金额(折扣券用)',
    start_time DATETIME NOT NULL COMMENT '生效时间',
    end_time DATETIME NOT NULL COMMENT '失效时间',
    total_quantity INT DEFAULT NULL COMMENT '发放总数(NULL表示不限)',
    received_count INT DEFAULT 0 COMMENT '已领取数量',
    per_user_limit INT DEFAULT 1 COMMENT '每人限领数量',
    is_vip_only TINYINT DEFAULT 0 COMMENT '是否VIP专属: 0-否 1-是',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用 1-正常',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_status (status),
    INDEX idx_time_range (start_time, end_time),
    INDEX idx_is_vip_only (is_vip_only)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='优惠券表';

-- ============================================================
-- 7. 用户优惠券表 (t_user_coupon)
-- ============================================================
DROP TABLE IF EXISTS t_user_coupon;
CREATE TABLE t_user_coupon (
    user_coupon_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户优惠券ID',
    user_id INT NOT NULL COMMENT '用户ID',
    coupon_id INT NOT NULL COMMENT '优惠券ID',
    status TINYINT DEFAULT 0 COMMENT '状态: 0-未使用 1-已使用 2-已过期',
    receive_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
    use_time DATETIME DEFAULT NULL COMMENT '使用时间',
    order_id BIGINT DEFAULT NULL COMMENT '使用的订单ID',
    
    INDEX idx_user_id (user_id),
    INDEX idx_coupon_id (coupon_id),
    INDEX idx_status (status),
    INDEX idx_order_id (order_id),
    
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES t_coupon(coupon_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户优惠券表';

-- ============================================================
-- 8. 订单表 (t_order)
-- ============================================================
DROP TABLE IF EXISTS t_order;
CREATE TABLE t_order (
    order_id BIGINT PRIMARY KEY COMMENT '订单号',
    user_id INT NOT NULL COMMENT '用户ID',
    
    -- 金额信息
    total_amount DECIMAL(10,2) NOT NULL COMMENT '商品总金额',
    freight_amount DECIMAL(10,2) DEFAULT 0 COMMENT '运费',
    discount_amount DECIMAL(10,2) DEFAULT 0 COMMENT '优惠券优惠金额',
    points_used INT DEFAULT 0 COMMENT '使用积分',
    points_discount DECIMAL(10,2) DEFAULT 0 COMMENT '积分抵扣金额',
    payment_amount DECIMAL(10,2) NOT NULL COMMENT '实付金额',
    
    -- 状态信息
    status TINYINT DEFAULT 0 COMMENT '订单状态: 0-待支付 1-已支付 2-已发货 3-已完成 4-已取消 5-已退款',
    
    -- 支付信息
    payment_method TINYINT DEFAULT NULL COMMENT '支付方式: 1-微信 2-支付宝 3-余额',
    payment_time DATETIME DEFAULT NULL COMMENT '支付时间',
    transaction_id VARCHAR(100) DEFAULT NULL COMMENT '第三方交易号',
    
    -- 物流信息
    shipping_company VARCHAR(50) DEFAULT NULL COMMENT '物流公司',
    shipping_number VARCHAR(100) DEFAULT NULL COMMENT '物流单号',
    shipping_time DATETIME DEFAULT NULL COMMENT '发货时间',
    receive_time DATETIME DEFAULT NULL COMMENT '收货时间',
    
    -- 地址快照(JSON格式存储完整地址信息)
    address_snapshot TEXT COMMENT '地址快照',
    
    -- 备注
    buyer_note VARCHAR(255) DEFAULT NULL COMMENT '买家备注',
    seller_note VARCHAR(255) DEFAULT NULL COMMENT '卖家备注',
    
    -- 时间
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_payment_time (payment_time),
    
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ============================================================
-- 9. 订单明细表 (t_order_item)
-- ============================================================
DROP TABLE IF EXISTS t_order_item;
CREATE TABLE t_order_item (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单明细ID',
    order_id BIGINT NOT NULL COMMENT '订单号',
    product_id INT NOT NULL COMMENT '商品ID',
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称(快照)',
    product_image VARCHAR(255) DEFAULT NULL COMMENT '商品图片(快照)',
    price DECIMAL(10,2) NOT NULL COMMENT '商品单价(快照)',
    quantity INT NOT NULL COMMENT '购买数量',
    subtotal DECIMAL(10,2) NOT NULL COMMENT '小计金额',
    is_reviewed TINYINT DEFAULT 0 COMMENT '是否已评价: 0-否 1-是',
    
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id),
    
    FOREIGN KEY (order_id) REFERENCES t_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES t_product(product_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单明细表';

-- ============================================================
-- 10. 评价表 (t_review)
-- ============================================================
DROP TABLE IF EXISTS t_review;
CREATE TABLE t_review (
    review_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    order_id BIGINT NOT NULL COMMENT '订单号',
    order_item_id INT NOT NULL COMMENT '订单明细ID',
    rating TINYINT NOT NULL COMMENT '评分: 1-5星',
    comment TEXT COMMENT '评价内容',
    images TEXT COMMENT '评价图片(JSON数组)',
    is_anonymous TINYINT DEFAULT 0 COMMENT '是否匿名: 0-否 1-是',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-待审核 1-已发布 2-已屏蔽',
    admin_reply TEXT COMMENT '管理员回复',
    reply_time DATETIME DEFAULT NULL COMMENT '回复时间',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    UNIQUE KEY uk_order_item (order_item_id),
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_order_id (order_id),
    INDEX idx_rating (rating),
    INDEX idx_create_time (create_time),
    
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES t_product(product_id) ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES t_order(order_id) ON DELETE RESTRICT,
    FOREIGN KEY (order_item_id) REFERENCES t_order_item(order_item_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品评价表';

-- ============================================================
-- 11. 积分流水表 (t_points_log)
-- ============================================================
DROP TABLE IF EXISTS t_points_log;
CREATE TABLE t_points_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水ID',
    user_id INT NOT NULL COMMENT '用户ID',
    type TINYINT NOT NULL COMMENT '类型: 1-收入 2-支出',
    amount INT NOT NULL COMMENT '积分数量',
    balance_after INT NOT NULL COMMENT '变动后余额',
    source VARCHAR(50) DEFAULT NULL COMMENT '来源: ORDER-订单 RECHARGE-充值 EXCHANGE-兑换 ADMIN-管理员',
    source_id VARCHAR(100) DEFAULT NULL COMMENT '来源ID(如订单号)',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_create_time (create_time),
    
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分流水表';

-- ============================================================
-- 12. 操作日志表 (t_operation_log)
-- ============================================================
DROP TABLE IF EXISTS t_operation_log;
CREATE TABLE t_operation_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    user_id INT DEFAULT NULL COMMENT '操作用户ID',
    user_type TINYINT DEFAULT 1 COMMENT '用户类型: 1-普通用户 2-管理员',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_desc VARCHAR(255) DEFAULT NULL COMMENT '操作描述',
    request_method VARCHAR(10) DEFAULT NULL COMMENT '请求方法',
    request_url VARCHAR(255) DEFAULT NULL COMMENT '请求URL',
    request_params TEXT COMMENT '请求参数',
    ip_address VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    user_agent VARCHAR(255) DEFAULT NULL COMMENT '用户代理',
    result TINYINT DEFAULT 1 COMMENT '结果: 0-失败 1-成功',
    error_msg TEXT COMMENT '错误信息',
    execute_time INT DEFAULT NULL COMMENT '执行时间(毫秒)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_create_time (create_time),
    INDEX idx_result (result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ============================================================
-- 创建视图：商品统计视图
-- ============================================================
CREATE OR REPLACE VIEW v_product_stats AS
SELECT 
    p.product_id,
    p.name,
    p.price,
    p.sold_count,
    p.stock,
    c.name AS category_name,
    COUNT(DISTINCT r.review_id) AS review_count,
    IFNULL(AVG(r.rating), 0) AS avg_rating
FROM t_product p
LEFT JOIN t_category c ON p.category_id = c.category_id
LEFT JOIN t_review r ON p.product_id = r.product_id AND r.status = 1
GROUP BY p.product_id;

-- ============================================================
-- 创建视图：订单统计视图
-- ============================================================
CREATE OR REPLACE VIEW v_order_stats AS
SELECT 
    DATE(create_time) AS order_date,
    COUNT(*) AS order_count,
    SUM(payment_amount) AS total_amount,
    AVG(payment_amount) AS avg_amount
FROM t_order
WHERE status IN (1, 2, 3)  -- 已支付、已发货、已完成
GROUP BY DATE(create_time);
