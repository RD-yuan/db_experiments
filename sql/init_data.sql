-- ============================================================
-- 电子商务平台初始数据
-- 创建时间: 2026-04-08
-- ============================================================

USE ecommerce_db;

-- ============================================================
-- 1. 插入管理员账户
-- 密码: admin123 (BCrypt加密后的值)
-- ============================================================
INSERT INTO t_user (username, password, phone, email, gender, status, is_vip) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.aOy6.uRKrJXEku', '13800000000', 'admin@example.com', 1, 1, 0);

-- ============================================================
-- 2. 插入测试用户
-- 密码: 123456 (BCrypt加密后的值)
-- ============================================================
INSERT INTO t_user (username, password, phone, email, gender, status, is_vip, points) VALUES
('张三', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '13811111111', 'zhangsan@example.com', 1, 1, 0, 100),
('李四', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '13822222222', 'lisi@example.com', 2, 1, 1, 500),
('王五', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '13833333333', 'wangwu@example.com', 1, 1, 0, 0);

-- ============================================================
-- 3. 插入商品分类
-- ============================================================
-- 一级分类
INSERT INTO t_category (name, parent_id, level, icon, sort_order, status) VALUES
('电子产品', 0, 1, 'icon-electronics', 1, 1),
('服装鞋帽', 0, 1, 'icon-clothes', 2, 1),
('食品饮料', 0, 1, 'icon-food', 3, 1),
('家居用品', 0, 1, 'icon-home', 4, 1),
('图书文具', 0, 1, 'icon-book', 5, 1);

-- 二级分类 - 电子产品
INSERT INTO t_category (name, parent_id, level, sort_order, status) VALUES
('手机', 1, 2, 1, 1),
('电脑', 1, 2, 2, 1),
('平板', 1, 2, 3, 1),
('耳机音箱', 1, 2, 4, 1);

-- 二级分类 - 服装鞋帽
INSERT INTO t_category (name, parent_id, level, sort_order, status) VALUES
('男装', 2, 2, 1, 1),
('女装', 2, 2, 2, 1),
('运动鞋', 2, 2, 3, 1),
('休闲鞋', 2, 2, 4, 1);

-- ============================================================
-- 4. 插入商品数据
-- ============================================================
INSERT INTO t_product (name, description, price, original_price, vip_price, stock, sold_count, category_id, brand, status, is_hot, is_new, is_recommend) VALUES
-- 手机
('iPhone 15 Pro Max 256GB', '苹果最新旗舰手机，A17 Pro芯片，钛金属边框', 9999.00, 9999.00, 9799.00, 100, 258, 6, 'Apple', 1, 1, 1, 1),
('华为 Mate 60 Pro', '麒麟9000S芯片，卫星通话，昆仑玻璃', 6999.00, 7499.00, 6799.00, 150, 520, 6, 'Huawei', 1, 1, 0, 1),
('小米14 Ultra', '徕卡影像，骁龙8 Gen3，IP68防水', 5999.00, 6499.00, 5799.00, 200, 380, 6, 'Xiaomi', 1, 0, 1, 1),

-- 电脑
('MacBook Pro 14 M3 Pro', 'M3 Pro芯片，18GB统一内存，512GB存储', 16999.00, 16999.00, 16499.00, 50, 89, 7, 'Apple', 1, 1, 1, 1),
('联想 ThinkPad X1 Carbon', '第11代酷睿i7，16GB内存，1TB SSD', 12999.00, 14999.00, 12499.00, 80, 156, 7, 'Lenovo', 1, 0, 0, 1),

-- 耳机
('AirPods Pro 2', '主动降噪，自适应通透模式，MagSafe充电', 1899.00, 1999.00, 1799.00, 500, 1250, 9, 'Apple', 1, 1, 0, 1),
('索尼 WH-1000XM5', '行业领先降噪，30小时续航，Hi-Res音质', 2499.00, 2999.00, 2399.00, 200, 456, 9, 'Sony', 1, 1, 0, 1),

-- 男装
('优衣库 男装 经典款T恤', '100%纯棉，舒适透气，多色可选', 79.00, 99.00, NULL, 1000, 3520, 10, 'UNIQLO', 1, 0, 0, 0),
('Nike 男款 运动卫衣', '柔软面料，经典款式，多色可选', 399.00, 499.00, 379.00, 300, 890, 10, 'Nike', 1, 0, 1, 1),

-- 女装
('ZARA 女装 连衣裙', '优雅设计，舒适面料，多款可选', 299.00, 399.00, NULL, 500, 1200, 11, 'ZARA', 1, 0, 0, 0),

-- 运动鞋
('Nike Air Max 270', '大气垫设计，舒适缓震，经典百搭', 899.00, 1099.00, 849.00, 400, 2360, 12, 'Nike', 1, 1, 0, 1),
('Adidas Ultra Boost 22', 'Boost缓震科技，Primeknit鞋面', 1299.00, 1499.00, 1199.00, 250, 980, 12, 'Adidas', 1, 0, 0, 1);

-- ============================================================
-- 5. 插入收货地址
-- ============================================================
INSERT INTO t_address (user_id, recipient_name, recipient_phone, province, city, district, detail_address, is_default) VALUES
(2, '张三', '13811111111', '北京市', '北京市', '海淀区', '西土城路10号北京邮电大学', 1),
(2, '张三', '13811111111', '北京市', '北京市', '朝阳区', '望京SOHO T1', 0),
(3, '李四', '13822222222', '上海市', '上海市', '浦东新区', '陆家嘴金融中心', 1);

-- ============================================================
-- 6. 插入优惠券
-- ============================================================
INSERT INTO t_coupon (name, type, value, min_order_amount, max_discount, start_time, end_time, total_quantity, per_user_limit, is_vip_only, status) VALUES
('新人专享券', 3, 20.00, 100.00, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 10000, 1, 0, 1),
('满200减30', 1, 30.00, 200.00, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH), 5000, 2, 0, 1),
('满500减80', 1, 80.00, 500.00, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH), 3000, 2, 0, 1),
('全场9折券', 2, 0.90, 100.00, 50.00, NOW(), DATE_ADD(NOW(), INTERVAL 3 MONTH), 2000, 1, 0, 1),
('VIP专享8折券', 2, 0.80, 200.00, 100.00, NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH), 1000, 1, 1, 1),
('VIP满1000减200', 1, 200.00, 1000.00, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH), 500, 1, 1, 1);

-- ============================================================
-- 7. 给用户发放优惠券
-- ============================================================
INSERT INTO t_user_coupon (user_id, coupon_id, status, receive_time) VALUES
(2, 1, 0, NOW()),  -- 张三领取新人券
(2, 2, 0, NOW()),  -- 张三领取满200减30
(3, 5, 0, NOW()),  -- 李四(VIP)领取VIP专享券
(3, 6, 0, NOW());  -- 李四(VIP)领取VIP满减券

-- ============================================================
-- 8. 插入购物车数据
-- ============================================================
INSERT INTO t_shopping_cart (user_id, product_id, quantity, selected) VALUES
(2, 1, 1, 1),   -- 张三购物车: iPhone 15 Pro Max
(2, 6, 2, 1),   -- 张三购物车: AirPods Pro 2 x2
(3, 4, 1, 1);   -- 李四购物车: MacBook Pro

-- ============================================================
-- 9. 插入测试订单
-- ============================================================
INSERT INTO t_order (order_id, user_id, total_amount, freight_amount, discount_amount, payment_amount, status, payment_method, payment_time, address_snapshot) VALUES
(2026040800001, 2, 899.00, 0.00, 30.00, 869.00, 3, 1, NOW() - INTERVAL 7 DAY, '{"name":"张三","phone":"13811111111","address":"北京市北京市海淀区西土城路10号北京邮电大学"}'),
(2026040800002, 3, 16999.00, 0.00, 200.00, 16799.00, 2, 2, NOW() - INTERVAL 2 DAY, '{"name":"李四","phone":"13822222222","address":"上海市上海市浦东新区陆家嘴金融中心"}');

-- ============================================================
-- 10. 插入订单明细
-- ============================================================
INSERT INTO t_order_item (order_id, product_id, product_name, product_image, price, quantity, subtotal, is_reviewed) VALUES
(2026040800001, 11, 'Nike Air Max 270', NULL, 899.00, 1, 899.00, 1),
(2026040800002, 4, 'MacBook Pro 14 M3 Pro', NULL, 16999.00, 1, 16999.00, 0);

-- ============================================================
-- 11. 插入评价数据
-- ============================================================
INSERT INTO t_review (user_id, product_id, order_id, order_item_id, rating, comment, status) VALUES
(2, 11, 2026040800001, 1, 5, '鞋子很舒服，穿着走路很轻松，大气垫缓震效果很好！物流也很快，第二天就到了。', 1);

-- ============================================================
-- 12. 插入积分流水
-- ============================================================
INSERT INTO t_points_log (user_id, type, amount, balance_after, source, source_id, description) VALUES
(2, 1, 100, 100, 'ORDER', '2026040800001', '购物赠送积分'),
(3, 1, 500, 500, 'ADMIN', NULL, '系统赠送VIP积分');

-- ============================================================
-- 13. 插入操作日志
-- ============================================================
INSERT INTO t_operation_log (user_id, user_type, operation_type, operation_desc, ip_address, result) VALUES
(1, 2, 'LOGIN', '管理员登录', '127.0.0.1', 1),
(2, 1, 'LOGIN', '用户登录', '192.168.1.100', 1),
(2, 1, 'CREATE_ORDER', '创建订单', '192.168.1.100', 1),
(2, 1, 'PAY_ORDER', '支付订单', '192.168.1.100', 1);

-- ============================================================
-- 完成提示
-- ============================================================
SELECT '初始数据插入完成!' AS message;
SELECT '用户数' AS item, COUNT(*) AS count FROM t_user
UNION ALL
SELECT '商品数', COUNT(*) FROM t_product
UNION ALL
SELECT '分类数', COUNT(*) FROM t_category
UNION ALL
SELECT '优惠券数', COUNT(*) FROM t_coupon
UNION ALL
SELECT '订单数', COUNT(*) FROM t_order;
