-- Add refund support.
USE ecommerce_db;

ALTER TABLE t_order
    ADD COLUMN refund_reason VARCHAR(500) COMMENT '退货原因',
    ADD COLUMN refund_remark VARCHAR(500) COMMENT '管理员备注';

DROP TABLE IF EXISTS t_refund;
CREATE TABLE t_refund (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    user_id INT NOT NULL,
    reason VARCHAR(500) NOT NULL,
    status TINYINT DEFAULT 0 COMMENT '0待审核 1已同意 2已拒绝',
    admin_id INT,
    remark VARCHAR(500),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    FOREIGN KEY (order_id) REFERENCES t_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES t_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
