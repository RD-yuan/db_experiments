-- Fix shopping cart unique constraint to allow same product with different SKUs.
USE ecommerce_db;

ALTER TABLE t_shopping_cart
    DROP INDEX uk_user_product;

UPDATE t_shopping_cart SET sku_id = 0 WHERE sku_id IS NULL;

ALTER TABLE t_shopping_cart
    MODIFY COLUMN sku_id INT NOT NULL DEFAULT 0 COMMENT 'SKU ID，0表示无规格';

-- sku_id 使用 0 表示无规格，避免 MySQL UNIQUE 允许多个 NULL 行。
ALTER TABLE t_shopping_cart
    ADD UNIQUE KEY uk_user_product_sku (user_id, product_id, sku_id);
