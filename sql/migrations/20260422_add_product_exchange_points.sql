-- Add product exchange points for the points mall feature.
-- Run once against databases created before this column was added.

ALTER TABLE t_product
    ADD COLUMN exchange_points INT NOT NULL DEFAULT 0 COMMENT '积分兑换所需积分，0表示不可兑换' AFTER vip_price,
    ADD INDEX idx_exchange_points (exchange_points);
