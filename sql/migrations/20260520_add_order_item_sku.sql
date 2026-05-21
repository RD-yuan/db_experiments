-- Add sku_id/sku_text to order items; sku_id to seckill products.
-- Safe to re-run: skips columns that already exist.
USE ecommerce_db;

-- Fix ShoppingCart sku_id: fill NULLs first, then enforce NOT NULL
UPDATE t_shopping_cart SET sku_id = 0 WHERE sku_id IS NULL;

-- OrderItem: add sku_id (skip if exists)
SET @col = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'ecommerce_db' AND TABLE_NAME = 't_order_item' AND COLUMN_NAME = 'sku_id');
SET @sql = IF(@col = 0,
    'ALTER TABLE t_order_item ADD COLUMN sku_id INT NOT NULL DEFAULT 0 AFTER product_image',
    'SELECT "sku_id already exists, skipping" AS msg');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- OrderItem: add sku_text (skip if exists)
SET @col = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'ecommerce_db' AND TABLE_NAME = 't_order_item' AND COLUMN_NAME = 'sku_text');
SET @sql = IF(@col = 0,
    'ALTER TABLE t_order_item ADD COLUMN sku_text VARCHAR(200) DEFAULT NULL AFTER sku_id',
    'SELECT "sku_text already exists, skipping" AS msg');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- SeckillProduct: add sku_id (skip if exists)
SET @col = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'ecommerce_db' AND TABLE_NAME = 't_seckill_product' AND COLUMN_NAME = 'sku_id');
SET @sql = IF(@col = 0,
    'ALTER TABLE t_seckill_product ADD COLUMN sku_id INT NOT NULL DEFAULT 0 AFTER product_id',
    'SELECT "sku_id already exists, skipping" AS msg');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 修复负数 locked_stock
UPDATE t_product SET locked_stock = 0 WHERE locked_stock < 0;
UPDATE t_product_sku SET locked_stock = 0 WHERE locked_stock < 0;

-- 重新同步有 SKU 的商品库存
UPDATE t_product p SET stock = (
  SELECT COALESCE(SUM(s.stock), 0) FROM t_product_sku s WHERE s.product_id = p.product_id
) WHERE p.has_sku = 1;
