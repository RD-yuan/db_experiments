-- Add user balance and explicit administrator flag for existing databases.
-- Run once against databases created before these columns were added.

USE ecommerce_db;

ALTER TABLE t_user
    ADD COLUMN balance DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额' AFTER points,
    ADD COLUMN is_admin TINYINT DEFAULT 0 COMMENT '是否管理员: 0-否 1-是' AFTER update_time,
    ADD INDEX idx_is_admin (is_admin);

UPDATE t_user
SET is_admin = 1
WHERE username = 'admin' OR user_id = 1;
