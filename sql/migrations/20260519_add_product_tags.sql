-- Add product tags for keyword search enhancement.
-- Run once against databases created before these tables were added.

USE ecommerce_db;

DROP TABLE IF EXISTS t_product_tag;
DROP TABLE IF EXISTS t_tag;

CREATE TABLE t_tag (
    tag_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '标签ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名称',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品标签表';

CREATE TABLE t_product_tag (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
    product_id INT NOT NULL COMMENT '商品ID',
    tag_id INT NOT NULL COMMENT '标签ID',
    UNIQUE KEY uk_product_tag (product_id, tag_id),
    INDEX idx_product_id (product_id),
    INDEX idx_tag_id (tag_id),
    FOREIGN KEY (product_id) REFERENCES t_product(product_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES t_tag(tag_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品标签关联表';

-- Seed common tags
INSERT INTO t_tag (name) VALUES
('旗舰'), ('性价比'), ('降噪'), ('运动'), ('休闲'), ('经典'),
('高性能'), ('新品'), ('蓝牙'), ('防水'), ('大屏'), ('长续航');

-- Assign tags to existing products
INSERT INTO t_product_tag (product_id, tag_id) VALUES
(1, 1), (1, 7), (1, 11),   -- iPhone 15 Pro: 旗舰, 高性能, 大屏
(2, 1), (2, 7), (2, 11),   -- 华为 Mate 60 Pro: 旗舰, 高性能, 大屏
(3, 2), (3, 7),             -- 小米14 Ultra: 性价比, 高性能
(4, 7), (4, 11),            -- MacBook Pro: 高性能, 大屏
(5, 7),                     -- ThinkPad: 高性能
(6, 3), (6, 9),             -- AirPods Pro 2: 降噪, 蓝牙
(7, 1), (7, 3), (7, 9),    -- Sony WH-1000XM5: 旗舰, 降噪, 蓝牙
(8, 6),                     -- 优衣库 T恤: 经典
(9, 4),                     -- Nike 卫衣: 运动
(11, 4),                    -- Nike Air Max: 运动
(12, 4);                    -- Adidas Ultra Boost: 运动

