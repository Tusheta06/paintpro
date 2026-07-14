-- ============================================================
-- PaintPro IMS - Collation Hotfix
-- Run this against your LIVE paintpro_db to fix Error 1270.
-- No data loss. No business logic changes.
-- ============================================================

USE paintpro_db;

-- Step 1: Recreate the view with explicit COLLATE on every
--         string literal produced by the CASE expression.
--         This is the immediate fix for Error 1270.
CREATE OR REPLACE VIEW vw_product_summary AS
SELECT
    p.id,
    p.sku,
    p.barcode,
    p.name,
    p.paint_type,
    p.color_name,
    p.color_hex,
    p.finish,
    p.pack_size,
    p.selling_price,
    p.cost_price,
    p.gst_percentage,
    p.current_stock,
    p.minimum_stock,
    p.maximum_stock,
    p.image_path,
    p.is_active,
    c.name  AS category_name,
    b.name  AS brand_name,
    s.name  AS supplier_name,
    CASE
        WHEN p.current_stock = 0                   THEN 'out_of_stock' COLLATE utf8mb4_0900_ai_ci
        WHEN p.current_stock <= p.minimum_stock    THEN 'low_stock'    COLLATE utf8mb4_0900_ai_ci
        ELSE                                             'in_stock'    COLLATE utf8mb4_0900_ai_ci
    END AS stock_status,
    (p.selling_price - p.cost_price) AS unit_profit,
    (p.current_stock * p.cost_price) AS stock_value
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN brands     b ON p.brand_id     = b.id
LEFT JOIN suppliers  s ON p.supplier_id  = s.id;

-- Step 2: Alter the database default collation to match MySQL 8.0.
--         This ensures all future tables and views inherit the
--         correct collation automatically.
ALTER DATABASE paintpro_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

-- Step 3: Convert every table's default collation.
--         CONVERT TO also re-collates all existing VARCHAR/TEXT columns.
ALTER TABLE roles             CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE users             CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE categories        CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE brands            CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE suppliers         CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE customers         CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE products          CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE purchases         CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE purchase_items    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE sales             CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE sale_items        CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE stock_logs        CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE activity_logs     CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE notifications     CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
ALTER TABLE settings          CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- Verification query - should return zero rows after the fix.
SELECT 'Collation check - all tables' AS test_label;
SELECT TABLE_NAME, TABLE_COLLATION
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'paintpro_db'
  AND TABLE_TYPE   = 'BASE TABLE'
  AND TABLE_COLLATION != 'utf8mb4_0900_ai_ci';
-- Zero rows = fully consistent. ✅
