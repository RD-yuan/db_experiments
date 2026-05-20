-- Add SKU / product specification support.
-- Run once against databases created before these tables were added.

USE ecommerce_db;

DROP TABLE IF EXISTS t_product_sku;
DROP TABLE IF EXISTS t_spec_value;
DROP TABLE IF EXISTS t_spec_template;

CREATE TABLE t_spec_template (
    template_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '规格模板ID',
    name VARCHAR(50) NOT NULL COMMENT '规格名称（如颜色、尺寸）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规格模板表';

CREATE TABLE t_spec_value (
    value_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '规格值ID',
    template_id INT NOT NULL COMMENT '所属模板ID',
    value VARCHAR(50) NOT NULL COMMENT '规格值（如红色、XL）',
    sort_order INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_template_id (template_id),
    FOREIGN KEY (template_id) REFERENCES t_spec_template(template_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规格值表';

CREATE TABLE t_product_sku (
    sku_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'SKU ID',
    product_id INT NOT NULL COMMENT '商品ID',
    spec_ids VARCHAR(500) NOT NULL COMMENT '规格值ID组合，JSON数组如[1,3]',
    spec_text VARCHAR(200) COMMENT '规格文字描述，如"红色 / XL"',
    price DECIMAL(10,2) COMMENT 'SKU价格（NULL则使用商品基础价）',
    stock INT NOT NULL DEFAULT 0 COMMENT 'SKU库存',
    locked_stock INT DEFAULT 0 COMMENT 'SKU锁定库存',
    image VARCHAR(255) COMMENT 'SKU图片',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用 1-启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_product_id (product_id),
    FOREIGN KEY (product_id) REFERENCES t_product(product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品SKU表';

ALTER TABLE t_product
    ADD COLUMN has_sku TINYINT NOT NULL DEFAULT 0 COMMENT '是否有多规格: 0-否 1-是' AFTER exchange_points,
    ADD INDEX idx_has_sku (has_sku);

-- Seed spec templates
INSERT INTO t_spec_template (name) VALUES ('颜色'), ('尺寸'), ('版本');

-- Seed common spec values
INSERT INTO t_spec_value (template_id, value, sort_order) VALUES
(1, '黑色', 1), (1, '白色', 2), (1, '红色', 3), (1, '蓝色', 4), (1, '深空灰', 5), (1, '星光色', 6),
(2, 'S', 1), (2, 'M', 2), (2, 'L', 3), (2, 'XL', 4), (2, 'XXL', 5),
(3, '标准版', 1), (3, 'Pro版', 2), (3, 'Ultra版', 3);
