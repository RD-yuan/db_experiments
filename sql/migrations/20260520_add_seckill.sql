-- Add flash sale / seckill support.
USE ecommerce_db;

DROP TABLE IF EXISTS t_seckill_product;
DROP TABLE IF EXISTS t_seckill_session;

CREATE TABLE t_seckill_session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '场次名称',
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status TINYINT DEFAULT 1 COMMENT '0禁用 1启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_time (start_time, end_time),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE t_seckill_product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    product_id INT NOT NULL,
    seckill_price DECIMAL(10,2) NOT NULL,
    seckill_stock INT NOT NULL DEFAULT 0,
    limit_per_user INT DEFAULT 1 COMMENT '每人限购数量',
    version INT DEFAULT 0 COMMENT '乐观锁版本号',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_product (product_id),
    UNIQUE KEY uk_session_product (session_id, product_id),
    FOREIGN KEY (session_id) REFERENCES t_seckill_session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES t_product(product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
