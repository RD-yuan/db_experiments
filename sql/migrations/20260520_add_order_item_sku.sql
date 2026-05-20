-- Add sku_id to order items for tracking which SKU was purchased.
USE ecommerce_db;

ALTER TABLE t_order_item
    ADD COLUMN sku_id INT DEFAULT NULL AFTER product_image;
-- 修复负数 locked_stock
UPDATE t_product SET locked_stock = 0 WHERE locked_stock < 0;
UPDATE t_product_sku SET locked_stock = 0 WHERE locked_stock < 0;

-- 重新同步有 SKU 的商品库存
UPDATE t_product p SET stock = (
  SELECT COALESCE(SUM(s.stock), 0) FROM t_product_sku s WHERE s.product_id = p.product_id
) WHERE p.has_sku = 1;