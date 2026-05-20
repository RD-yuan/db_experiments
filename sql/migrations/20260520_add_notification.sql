-- Add notification / announcement support.
USE ecommerce_db;

DROP TABLE IF EXISTS t_notification;
CREATE TABLE t_notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    type TINYINT NOT NULL DEFAULT 1 COMMENT '1系统公告 2个人消息',
    user_id INT COMMENT '个人消息时为接收用户ID，公告为NULL',
    is_read TINYINT DEFAULT 0 COMMENT '0未读 1已读',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_type (user_id, type),
    INDEX idx_create_time (create_time),
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE t_shopping_cart ADD COLUMN sku_id INT DEFAULT NULL AFTER product_id;
