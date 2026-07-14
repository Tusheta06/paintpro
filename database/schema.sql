-- ============================================================
-- PaintPro Inventory Management System
-- MySQL Database Schema  |  Version 1.0.0
-- ============================================================
-- Encoding  : utf8mb4 (full Unicode + emoji support)
-- Collation : utf8mb4_0900_ai_ci  (MySQL 8.0 default)
-- Engine    : InnoDB (ACID, FK, row-level locking)
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- ============================================================
-- Create and select the database
-- ============================================================
CREATE DATABASE IF NOT EXISTS paintpro_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE paintpro_db;


-- ============================================================
-- TABLE 1: roles
-- Defines user roles and their JSON-encoded permissions.
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name        VARCHAR(50)     NOT NULL,               -- e.g. admin, manager, employee
    display_name VARCHAR(100)   NOT NULL,               -- e.g. Administrator
    description TEXT            DEFAULT NULL,
    permissions JSON            DEFAULT NULL,           -- JSON array of allowed page keys
    is_active   TINYINT(1)      NOT NULL DEFAULT 1,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='User role definitions with RBAC permission lists';


-- ============================================================
-- TABLE 2: users
-- Stores all user accounts.  Passwords are bcrypt-hashed.
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    role_id         INT UNSIGNED    NOT NULL,
    full_name       VARCHAR(150)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    phone           VARCHAR(20)     DEFAULT NULL,
    password_hash   VARCHAR(255)    NOT NULL,           -- bcrypt hash
    avatar_path     VARCHAR(500)    DEFAULT NULL,       -- relative path to uploaded image
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    is_verified     TINYINT(1)      NOT NULL DEFAULT 0,
    last_login      DATETIME        DEFAULT NULL,
    login_attempts  TINYINT         NOT NULL DEFAULT 0,
    locked_until    DATETIME        DEFAULT NULL,
    reset_token     VARCHAR(255)    DEFAULT NULL,
    reset_token_expires DATETIME    DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by      INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email),
    INDEX  idx_users_role_id   (role_id),
    INDEX  idx_users_is_active (is_active),
    INDEX  idx_users_email     (email),

    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='User accounts with bcrypt-hashed passwords and role assignment';


-- ============================================================
-- TABLE 3: categories
-- Hierarchical product categories (supports parent-child).
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    parent_id   INT UNSIGNED    DEFAULT NULL,           -- NULL = top-level category
    name        VARCHAR(100)    NOT NULL,
    slug        VARCHAR(120)    NOT NULL,               -- URL-safe identifier
    description TEXT            DEFAULT NULL,
    icon        VARCHAR(100)    DEFAULT NULL,           -- Font Awesome class or emoji
    color_hex   VARCHAR(7)      DEFAULT '#6C63FF',      -- Category accent color
    sort_order  SMALLINT        NOT NULL DEFAULT 0,
    is_active   TINYINT(1)      NOT NULL DEFAULT 1,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by  INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_slug (slug),
    INDEX  idx_categories_parent   (parent_id),
    INDEX  idx_categories_active   (is_active),

    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id) REFERENCES categories(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_categories_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Hierarchical product categories with parent-child support';


-- ============================================================
-- TABLE 4: brands
-- Paint manufacturer / brand catalog.
-- ============================================================
CREATE TABLE IF NOT EXISTS brands (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name            VARCHAR(150)    NOT NULL,
    slug            VARCHAR(160)    NOT NULL,
    logo_path       VARCHAR(500)    DEFAULT NULL,
    website         VARCHAR(300)    DEFAULT NULL,
    description     TEXT            DEFAULT NULL,
    country         VARCHAR(100)    DEFAULT 'India',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    sort_order      SMALLINT        NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by      INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_brands_slug (slug),
    INDEX idx_brands_active (is_active),

    CONSTRAINT fk_brands_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Paint brand catalog with logo and metadata';


-- ============================================================
-- TABLE 5: suppliers
-- Supplier / vendor master data.
-- ============================================================
CREATE TABLE IF NOT EXISTS suppliers (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name                VARCHAR(200)    NOT NULL,
    contact_person      VARCHAR(150)    DEFAULT NULL,
    email               VARCHAR(255)    DEFAULT NULL,
    phone               VARCHAR(20)     NOT NULL,
    alternate_phone     VARCHAR(20)     DEFAULT NULL,
    gst_number          VARCHAR(20)     DEFAULT NULL,
    pan_number          VARCHAR(15)     DEFAULT NULL,
    address_line1       VARCHAR(255)    DEFAULT NULL,
    address_line2       VARCHAR(255)    DEFAULT NULL,
    city                VARCHAR(100)    DEFAULT NULL,
    state               VARCHAR(100)    DEFAULT NULL,
    pincode             VARCHAR(10)     DEFAULT NULL,
    country             VARCHAR(100)    NOT NULL DEFAULT 'India',
    bank_name           VARCHAR(150)    DEFAULT NULL,
    bank_account        VARCHAR(50)     DEFAULT NULL,
    bank_ifsc           VARCHAR(20)     DEFAULT NULL,
    credit_limit        DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    outstanding_balance DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    payment_terms_days  SMALLINT        NOT NULL DEFAULT 30,
    notes               TEXT            DEFAULT NULL,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by          INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    INDEX idx_suppliers_name   (name),
    INDEX idx_suppliers_active (is_active),
    INDEX idx_suppliers_gst    (gst_number),

    CONSTRAINT fk_suppliers_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Supplier / vendor master with financial terms and balance tracking';


-- ============================================================
-- TABLE 6: customers
-- Customer / buyer master data.
-- ============================================================
CREATE TABLE IF NOT EXISTS customers (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name                VARCHAR(200)    NOT NULL,
    customer_type       ENUM('individual','business') NOT NULL DEFAULT 'individual',
    email               VARCHAR(255)    DEFAULT NULL,
    phone               VARCHAR(20)     NOT NULL,
    alternate_phone     VARCHAR(20)     DEFAULT NULL,
    gst_number          VARCHAR(20)     DEFAULT NULL,
    address_line1       VARCHAR(255)    DEFAULT NULL,
    address_line2       VARCHAR(255)    DEFAULT NULL,
    city                VARCHAR(100)    DEFAULT NULL,
    state               VARCHAR(100)    DEFAULT NULL,
    pincode             VARCHAR(10)     DEFAULT NULL,
    country             VARCHAR(100)    NOT NULL DEFAULT 'India',
    credit_limit        DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    outstanding_amount  DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    loyalty_points      INT             NOT NULL DEFAULT 0,
    notes               TEXT            DEFAULT NULL,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by          INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    INDEX idx_customers_name   (name),
    INDEX idx_customers_phone  (phone),
    INDEX idx_customers_active (is_active),
    INDEX idx_customers_gst    (gst_number),

    CONSTRAINT fk_customers_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Customer master with credit limit and outstanding balance tracking';


-- ============================================================
-- TABLE 7: products
-- Core paint product catalog with all inventory attributes.
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    category_id         INT UNSIGNED    DEFAULT NULL,
    brand_id            INT UNSIGNED    DEFAULT NULL,
    manufacturer        VARCHAR(200)    DEFAULT NULL,
    supplier_id         INT UNSIGNED    DEFAULT NULL,

    -- Identification
    sku                 VARCHAR(100)    NOT NULL,        -- Stock Keeping Unit
    barcode             VARCHAR(100)    DEFAULT NULL,
    qr_code_data        TEXT            DEFAULT NULL,

    -- Basic Info
    name                VARCHAR(300)    NOT NULL,
    slug                VARCHAR(320)    NOT NULL,
    description         TEXT            DEFAULT NULL,

    -- Paint-specific attributes
    paint_type          VARCHAR(100)    DEFAULT NULL,   -- Interior, Exterior, etc.
    color_name          VARCHAR(150)    DEFAULT NULL,   -- e.g. "Ivory White"
    color_hex           VARCHAR(7)      DEFAULT NULL,   -- e.g. "#FFFFF0"
    color_rgb           VARCHAR(20)     DEFAULT NULL,   -- e.g. "255,255,240"
    finish              VARCHAR(50)     DEFAULT NULL,   -- Matte, Gloss, Satin, etc.
    pack_size           VARCHAR(50)     DEFAULT NULL,   -- 1L, 4L, 10L, etc.

    -- Pricing
    cost_price          DECIMAL(12,2)   NOT NULL DEFAULT 0.00,  -- Purchase price
    selling_price       DECIMAL(12,2)   NOT NULL DEFAULT 0.00,  -- MRP / selling price
    gst_percentage      DECIMAL(5,2)    NOT NULL DEFAULT 18.00,
    discount_percentage DECIMAL(5,2)    NOT NULL DEFAULT 0.00,

    -- Stock
    current_stock       DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    minimum_stock       DECIMAL(10,2)   NOT NULL DEFAULT 5.00,   -- Reorder level
    maximum_stock       DECIMAL(10,2)   NOT NULL DEFAULT 100.00,
    reorder_quantity    DECIMAL(10,2)   NOT NULL DEFAULT 10.00,
    unit                VARCHAR(20)     NOT NULL DEFAULT 'unit', -- unit, litre, kg, etc.

    -- Location & expiry
    storage_location    VARCHAR(200)    DEFAULT NULL,
    expiry_date         DATE            DEFAULT NULL,
    manufacture_date    DATE            DEFAULT NULL,

    -- Media
    image_path          VARCHAR(500)    DEFAULT NULL,

    -- Status
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    is_featured         TINYINT(1)      NOT NULL DEFAULT 0,

    -- Timestamps
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by          INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_products_sku    (sku),
    UNIQUE KEY uq_products_slug   (slug),
    INDEX idx_products_barcode    (barcode),
    INDEX idx_products_category   (category_id),
    INDEX idx_products_brand      (brand_id),
    INDEX idx_products_supplier   (supplier_id),
    INDEX idx_products_active     (is_active),
    INDEX idx_products_stock      (current_stock),
    INDEX idx_products_name       (name(100)),
    FULLTEXT INDEX ft_products_search (name, description, color_name, sku),

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_products_brand
        FOREIGN KEY (brand_id) REFERENCES brands(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_products_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    CONSTRAINT chk_products_prices
        CHECK (selling_price >= 0 AND cost_price >= 0),
    CONSTRAINT chk_products_stock
        CHECK (current_stock >= 0 AND minimum_stock >= 0 AND maximum_stock >= minimum_stock),
    CONSTRAINT chk_products_gst
        CHECK (gst_percentage IN (0, 5, 12, 18, 28))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Core paint product catalog with pricing, stock, and color metadata';


-- ============================================================
-- TABLE 8: purchases
-- Purchase order header (one row per PO).
-- ============================================================
CREATE TABLE IF NOT EXISTS purchases (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    supplier_id     INT UNSIGNED    NOT NULL,
    created_by      INT UNSIGNED    DEFAULT NULL,

    -- Reference numbers
    po_number       VARCHAR(50)     NOT NULL,           -- e.g. PO-2024-0001
    supplier_invoice_no VARCHAR(100) DEFAULT NULL,

    -- Dates
    order_date      DATE            NOT NULL,
    expected_date   DATE            DEFAULT NULL,
    received_date   DATE            DEFAULT NULL,

    -- Financial
    subtotal        DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    gst_amount      DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    shipping_cost   DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    grand_total     DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    paid_amount     DECIMAL(14,2)   NOT NULL DEFAULT 0.00,

    -- Status
    status          ENUM('draft','ordered','partial','received','cancelled')
                    NOT NULL DEFAULT 'draft',
    payment_status  ENUM('unpaid','partial','paid')
                    NOT NULL DEFAULT 'unpaid',

    notes           TEXT            DEFAULT NULL,
    invoice_path    VARCHAR(500)    DEFAULT NULL,       -- uploaded supplier invoice scan

    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_purchases_po_number (po_number),
    INDEX idx_purchases_supplier  (supplier_id),
    INDEX idx_purchases_status    (status),
    INDEX idx_purchases_date      (order_date),
    INDEX idx_purchases_creator   (created_by),

    CONSTRAINT fk_purchases_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_purchases_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Purchase order headers with financial totals and status tracking';


-- ============================================================
-- TABLE 9: purchase_items
-- Line items for each purchase order.
-- ============================================================
CREATE TABLE IF NOT EXISTS purchase_items (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    purchase_id     INT UNSIGNED    NOT NULL,
    product_id      INT UNSIGNED    NOT NULL,

    quantity_ordered    DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    quantity_received   DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    unit_cost           DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    gst_percentage      DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    gst_amount          DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    discount_percentage DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    discount_amount     DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    line_total          DECIMAL(14,2)   NOT NULL DEFAULT 0.00,

    -- Quality control
    damaged_quantity    DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    notes               TEXT            DEFAULT NULL,

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_purchase_items_purchase (purchase_id),
    INDEX idx_purchase_items_product  (product_id),

    CONSTRAINT fk_purchase_items_purchase
        FOREIGN KEY (purchase_id) REFERENCES purchases(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_purchase_items_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT chk_purchase_items_qty
        CHECK (quantity_ordered >= 0 AND quantity_received >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Line items for purchase orders with quantity tracking';


-- ============================================================
-- TABLE 10: sales
-- Sales invoice header.
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    customer_id     INT UNSIGNED    DEFAULT NULL,       -- NULL = walk-in customer
    created_by      INT UNSIGNED    DEFAULT NULL,

    -- Reference
    invoice_number  VARCHAR(50)     NOT NULL,           -- e.g. INV-2024-0001
    invoice_date    DATE            NOT NULL,
    due_date        DATE            DEFAULT NULL,

    -- Customer (denormalized for walk-in & invoice persistence)
    customer_name   VARCHAR(200)    DEFAULT 'Walk-in Customer',
    customer_phone  VARCHAR(20)     DEFAULT NULL,
    customer_email  VARCHAR(255)    DEFAULT NULL,
    customer_gst    VARCHAR(20)     DEFAULT NULL,
    customer_address TEXT           DEFAULT NULL,

    -- Financial
    subtotal        DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    discount_type   ENUM('percentage','fixed') NOT NULL DEFAULT 'percentage',
    discount_value  DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    gst_amount      DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    grand_total     DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    paid_amount     DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    balance_due     DECIMAL(14,2)   NOT NULL DEFAULT 0.00,

    -- Payment
    payment_method  ENUM('cash','card','upi','bank_transfer','cheque','credit')
                    NOT NULL DEFAULT 'cash',
    payment_status  ENUM('paid','unpaid','partial','overdue','cancelled','refunded')
                    NOT NULL DEFAULT 'unpaid',
    payment_date    DATE            DEFAULT NULL,

    -- Status
    status          ENUM('draft','confirmed','shipped','delivered','cancelled','returned')
                    NOT NULL DEFAULT 'confirmed',

    notes           TEXT            DEFAULT NULL,
    pdf_path        VARCHAR(500)    DEFAULT NULL,

    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_sales_invoice_number (invoice_number),
    INDEX idx_sales_customer      (customer_id),
    INDEX idx_sales_date          (invoice_date),
    INDEX idx_sales_payment_status(payment_status),
    INDEX idx_sales_status        (status),
    INDEX idx_sales_creator       (created_by),
    FULLTEXT INDEX ft_sales_search (invoice_number, customer_name),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_sales_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Sales invoice headers with full financial and payment tracking';


-- ============================================================
-- TABLE 11: sale_items
-- Line items for each sales invoice.
-- ============================================================
CREATE TABLE IF NOT EXISTS sale_items (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    sale_id             INT UNSIGNED    NOT NULL,
    product_id          INT UNSIGNED    NOT NULL,

    -- Denormalized snapshot at time of sale
    product_name        VARCHAR(300)    NOT NULL,
    product_sku         VARCHAR(100)    DEFAULT NULL,
    color_name          VARCHAR(150)    DEFAULT NULL,
    pack_size           VARCHAR(50)     DEFAULT NULL,

    quantity            DECIMAL(10,2)   NOT NULL DEFAULT 1.00,
    unit_price          DECIMAL(12,2)   NOT NULL DEFAULT 0.00,   -- selling price at time of sale
    cost_price          DECIMAL(12,2)   NOT NULL DEFAULT 0.00,   -- cost at time of sale (for profit calc)
    discount_percentage DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    discount_amount     DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    gst_percentage      DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    gst_amount          DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    line_total          DECIMAL(14,2)   NOT NULL DEFAULT 0.00,   -- after discount + GST

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_sale_items_sale    (sale_id),
    INDEX idx_sale_items_product (product_id),

    CONSTRAINT fk_sale_items_sale
        FOREIGN KEY (sale_id) REFERENCES sales(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_sale_items_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT chk_sale_items_qty
        CHECK (quantity > 0),
    CONSTRAINT chk_sale_items_price
        CHECK (unit_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Sales invoice line items with denormalized product snapshot for audit';


-- ============================================================
-- TABLE 12: stock_logs
-- Complete inventory movement audit trail.
-- ============================================================
CREATE TABLE IF NOT EXISTS stock_logs (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    product_id      INT UNSIGNED    NOT NULL,
    user_id         INT UNSIGNED    DEFAULT NULL,

    -- Reference to triggering transaction
    reference_type  ENUM('purchase','sale','adjustment','return_in','return_out',
                         'damaged','opening','transfer') NOT NULL,
    reference_id    INT UNSIGNED    DEFAULT NULL,       -- FK to purchases.id / sales.id

    -- Stock movement
    quantity_before DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    quantity_change DECIMAL(10,2)   NOT NULL,           -- +ve = stock in, -ve = stock out
    quantity_after  DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    unit_cost       DECIMAL(12,2)   DEFAULT NULL,       -- cost at time of movement

    -- Location
    from_location   VARCHAR(200)    DEFAULT NULL,
    to_location     VARCHAR(200)    DEFAULT NULL,

    notes           TEXT            DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_stock_logs_product   (product_id),
    INDEX idx_stock_logs_user      (user_id),
    INDEX idx_stock_logs_ref_type  (reference_type, reference_id),
    INDEX idx_stock_logs_date      (created_at),

    CONSTRAINT fk_stock_logs_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_stock_logs_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Complete inventory movement log - every stock change is recorded here';


-- ============================================================
-- TABLE 13: activity_logs
-- User activity and system audit trail.
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    user_id         INT UNSIGNED    DEFAULT NULL,
    action          VARCHAR(100)    NOT NULL,           -- e.g. 'create_product'
    module          VARCHAR(50)     NOT NULL,           -- e.g. 'inventory'
    description     TEXT            DEFAULT NULL,
    entity_type     VARCHAR(50)     DEFAULT NULL,       -- e.g. 'product'
    entity_id       INT UNSIGNED    DEFAULT NULL,
    old_values      JSON            DEFAULT NULL,       -- before state snapshot
    new_values      JSON            DEFAULT NULL,       -- after state snapshot
    ip_address      VARCHAR(45)     DEFAULT NULL,
    user_agent      VARCHAR(500)    DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_activity_logs_user   (user_id),
    INDEX idx_activity_logs_module (module),
    INDEX idx_activity_logs_action (action),
    INDEX idx_activity_logs_date   (created_at),
    INDEX idx_activity_logs_entity (entity_type, entity_id),

    CONSTRAINT fk_activity_logs_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Full user activity and system audit trail with before/after state snapshots';


-- ============================================================
-- TABLE 14: notifications
-- In-app notification center.
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    user_id         INT UNSIGNED    DEFAULT NULL,       -- NULL = broadcast to all
    type            VARCHAR(50)     NOT NULL,           -- low_stock, new_sale, etc.
    title           VARCHAR(255)    NOT NULL,
    message         TEXT            NOT NULL,
    icon            VARCHAR(100)    DEFAULT NULL,
    color           VARCHAR(7)      DEFAULT '#6C63FF',
    priority        ENUM('low','normal','high','critical') NOT NULL DEFAULT 'normal',
    is_read         TINYINT(1)      NOT NULL DEFAULT 0,
    read_at         DATETIME        DEFAULT NULL,
    action_url      VARCHAR(500)    DEFAULT NULL,       -- deep-link to relevant page
    reference_type  VARCHAR(50)     DEFAULT NULL,
    reference_id    INT UNSIGNED    DEFAULT NULL,
    expires_at      DATETIME        DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_notifications_user     (user_id),
    INDEX idx_notifications_type     (type),
    INDEX idx_notifications_is_read  (is_read),
    INDEX idx_notifications_created  (created_at),
    INDEX idx_notifications_priority (priority),

    CONSTRAINT fk_notifications_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='In-app notification center with priority levels and read tracking';


-- ============================================================
-- TABLE 15: settings
-- Application-wide key-value configuration store.
-- ============================================================
CREATE TABLE IF NOT EXISTS settings (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    setting_key     VARCHAR(100)    NOT NULL,
    setting_value   TEXT            DEFAULT NULL,
    setting_type    ENUM('string','integer','decimal','boolean','json','color','text')
                    NOT NULL DEFAULT 'string',
    category        VARCHAR(50)     NOT NULL DEFAULT 'general',
    label           VARCHAR(200)    DEFAULT NULL,       -- Human-readable label
    description     TEXT            DEFAULT NULL,
    is_public       TINYINT(1)      NOT NULL DEFAULT 0, -- Whether visible to non-admins
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      INT UNSIGNED    DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_settings_key (setting_key),
    INDEX idx_settings_category (category),

    CONSTRAINT fk_settings_updater
        FOREIGN KEY (updated_by) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Application configuration key-value store with typed values';


-- ============================================================
-- VIEWS
-- ============================================================

-- View: Product summary with computed stock status
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
        WHEN p.current_stock <= p.minimum_stock    THEN 'low_stock' COLLATE utf8mb4_0900_ai_ci
        ELSE                                             'in_stock' COLLATE utf8mb4_0900_ai_ci
    END AS stock_status,
    (p.selling_price - p.cost_price) AS unit_profit,
    (p.current_stock * p.cost_price) AS stock_value
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN brands     b ON p.brand_id     = b.id
LEFT JOIN suppliers  s ON p.supplier_id  = s.id;


-- View: Sales with customer and creator info
CREATE OR REPLACE VIEW vw_sales_summary AS
SELECT
    s.id,
    s.invoice_number,
    s.invoice_date,
    s.customer_name,
    s.grand_total,
    s.paid_amount,
    s.balance_due,
    s.payment_status,
    s.payment_method,
    s.status,
    u.full_name AS created_by_name,
    cust.phone  AS customer_phone,
    (s.grand_total - s.gst_amount - s.discount_amount) AS taxable_value
FROM sales s
LEFT JOIN users     u    ON s.created_by  = u.id
LEFT JOIN customers cust ON s.customer_id = cust.id;


-- View: Purchase with supplier info
CREATE OR REPLACE VIEW vw_purchases_summary AS
SELECT
    p.id,
    p.po_number,
    p.order_date,
    p.received_date,
    p.grand_total,
    p.paid_amount,
    p.status,
    p.payment_status,
    sup.name        AS supplier_name,
    sup.phone       AS supplier_phone,
    u.full_name     AS created_by_name
FROM purchases p
LEFT JOIN suppliers sup ON p.supplier_id = sup.id
LEFT JOIN users     u   ON p.created_by  = u.id;


-- View: Dashboard KPI snapshot
CREATE OR REPLACE VIEW vw_dashboard_kpis AS
SELECT
    (SELECT COUNT(*) FROM products  WHERE is_active = 1)  AS total_products,
    (SELECT COUNT(*) FROM categories WHERE is_active = 1) AS total_categories,
    (SELECT COUNT(*) FROM brands    WHERE is_active = 1)  AS total_brands,
    (SELECT COUNT(*) FROM customers WHERE is_active = 1)  AS total_customers,
    (SELECT COUNT(*) FROM suppliers WHERE is_active = 1)  AS total_suppliers,
    (SELECT COUNT(*) FROM sales     WHERE status != 'cancelled') AS total_sales,
    (SELECT COUNT(*) FROM purchases WHERE status != 'cancelled') AS total_purchases,
    (SELECT COALESCE(SUM(grand_total),0) FROM sales
         WHERE DATE(invoice_date) = CURDATE()
           AND status != 'cancelled')  AS today_revenue,
    (SELECT COALESCE(SUM(grand_total),0) FROM sales
         WHERE MONTH(invoice_date) = MONTH(CURDATE())
           AND YEAR(invoice_date)  = YEAR(CURDATE())
           AND status != 'cancelled') AS monthly_revenue,
    (SELECT COALESCE(SUM(current_stock * cost_price),0) FROM products WHERE is_active = 1) AS inventory_value,
    (SELECT COUNT(*) FROM products WHERE current_stock <= minimum_stock AND is_active = 1) AS low_stock_count,
    (SELECT COUNT(*) FROM products WHERE current_stock  = 0 AND is_active = 1)             AS out_of_stock_count,
    (SELECT COUNT(*) FROM sales WHERE payment_status IN ('unpaid','partial'))               AS pending_payments;


-- ============================================================
-- TRIGGERS
-- ============================================================

DELIMITER //

-- Trigger: Auto-update product stock after purchase_items insert
CREATE TRIGGER trg_purchase_item_insert
AFTER INSERT ON purchase_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock + NEW.quantity_received,
        updated_at    = NOW()
    WHERE id = NEW.product_id;
END //


-- Trigger: Auto-update product stock after sale_items insert (decrement)
CREATE TRIGGER trg_sale_item_insert
AFTER INSERT ON sale_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock - NEW.quantity,
        updated_at    = NOW()
    WHERE id = NEW.product_id;
END //


-- Trigger: Recalculate sales balance_due after payment_status update
CREATE TRIGGER trg_sales_balance_update
BEFORE UPDATE ON sales
FOR EACH ROW
BEGIN
    SET NEW.balance_due = NEW.grand_total - NEW.paid_amount;
END //


-- Trigger: Auto-generate invoice number if empty on insert
CREATE TRIGGER trg_sales_invoice_number
BEFORE INSERT ON sales
FOR EACH ROW
BEGIN
    IF NEW.invoice_number IS NULL OR NEW.invoice_number = '' THEN
        SET NEW.invoice_number = CONCAT(
            'INV-',
            YEAR(NOW()),
            '-',
            LPAD((SELECT COALESCE(MAX(id), 0) + 1 FROM sales), 5, '0')
        );
    END IF;
END //


-- Trigger: Auto-generate PO number if empty on insert
CREATE TRIGGER trg_purchase_po_number
BEFORE INSERT ON purchases
FOR EACH ROW
BEGIN
    IF NEW.po_number IS NULL OR NEW.po_number = '' THEN
        SET NEW.po_number = CONCAT(
            'PO-',
            YEAR(NOW()),
            '-',
            LPAD((SELECT COALESCE(MAX(id), 0) + 1 FROM purchases), 5, '0')
        );
    END IF;
END //

DELIMITER ;


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- End of Schema
-- ============================================================
