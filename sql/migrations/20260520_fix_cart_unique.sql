-- Fix shopping cart unique constraint to allow same product with different SKUs.
USE ecommerce_db;

ALTER TABLE t_shopping_cart
    DROP INDEX uk_user_product;

-- MySQL treats NULL sku_id values as distinct, so non-SKU products still get one row per user.
ALTER TABLE t_shopping_cart
    ADD UNIQUE KEY uk_user_product_sku (user_id, product_id, sku_id);
