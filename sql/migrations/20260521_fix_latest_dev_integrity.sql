-- Fix schema drift introduced by SKU, seckill, refund, and notification updates.
USE ecommerce_db;

UPDATE t_shopping_cart SET sku_id = 0 WHERE sku_id IS NULL;

ALTER TABLE t_shopping_cart
    MODIFY COLUMN sku_id INT NOT NULL DEFAULT 0 COMMENT 'SKU ID，0表示无规格';

UPDATE t_order_item SET sku_id = 0 WHERE sku_id IS NULL;

ALTER TABLE t_order_item
    MODIFY COLUMN sku_id INT NOT NULL DEFAULT 0 COMMENT 'SKU ID，0表示无规格',
    ADD COLUMN sku_text VARCHAR(200) DEFAULT NULL COMMENT 'SKU规格快照' AFTER sku_id,
    ADD INDEX idx_sku_id (sku_id);

ALTER TABLE t_seckill_product
    ADD COLUMN sku_id INT NOT NULL DEFAULT 0 COMMENT 'SKU ID，0表示无规格' AFTER product_id,
    ADD INDEX idx_sku_id (sku_id);

ALTER TABLE t_seckill_product
    DROP INDEX uk_session_product,
    ADD UNIQUE KEY uk_session_product_sku (session_id, product_id, sku_id);

CREATE TABLE IF NOT EXISTS t_notification_read (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    notification_id INT NOT NULL COMMENT '通知ID',
    user_id INT NOT NULL COMMENT '用户ID',
    read_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '已读时间',
    UNIQUE KEY uk_notification_user_read (notification_id, user_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (notification_id) REFERENCES t_notification(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统公告已读表';
