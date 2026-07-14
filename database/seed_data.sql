-- ============================================================
-- PaintPro Inventory Management System
-- Seed Data  |  Version 1.0.0
-- ============================================================
-- Run AFTER schema.sql
-- Provides: roles, default admin user, categories, brands,
--           sample suppliers, customers, products, and settings
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- ROLES
-- ============================================================
INSERT INTO roles (name, display_name, description, permissions, is_active) VALUES
('admin', 'Administrator',
 'Full system access - can manage users, settings, and all modules.',
 '["dashboard","inventory","categories","brands","suppliers","customers","purchases","sales","stock_management","reports","analytics","user_management","notifications","export_center","settings","profile"]',
 1),
('manager', 'Manager',
 'Operational access - can manage inventory, sales, purchases, and reports.',
 '["dashboard","inventory","categories","brands","suppliers","customers","purchases","sales","stock_management","reports","analytics","notifications","export_center","profile"]',
 1),
('employee', 'Employee',
 'Limited access - can view dashboard, manage sales, and update stock.',
 '["dashboard","inventory","customers","sales","stock_management","notifications","profile"]',
 1);


-- ============================================================
-- USERS  (password: Admin@123 - bcrypt hash below)
-- ============================================================
-- Note: The hash below corresponds to 'Admin@123' with bcrypt cost=12
-- When running the Python migration, bcrypt.hashpw() is used instead.
INSERT INTO users (role_id, full_name, email, phone, password_hash, is_active, is_verified)
VALUES
(1, 'System Administrator', 'admin@paintpro.com', '9876543210',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFhP.default.hash', 1, 1),
(2, 'Store Manager',        'manager@paintpro.com', '9876543211',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFhP.default.hash', 1, 1),
(3, 'Sales Employee',       'employee@paintpro.com', '9876543212',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFhP.default.hash', 1, 1);

-- NOTE: The Python migration script (migrations.py) will re-insert
-- users with properly generated bcrypt hashes. These are placeholders.


-- ============================================================
-- CATEGORIES
-- ============================================================
INSERT INTO categories (name, slug, description, icon, color_hex, sort_order, is_active) VALUES
('Interior Paints',    'interior-paints',    'Paints designed for indoor walls and ceilings',          'fa-home',        '#6C63FF', 1, 1),
('Exterior Paints',    'exterior-paints',    'Weather-resistant paints for outdoor surfaces',           'fa-building',    '#FF6B6B', 2, 1),
('Wood Finishes',      'wood-finishes',      'Varnishes, stains, and paints for wooden surfaces',       'fa-tree',        '#00D4AA', 3, 1),
('Metal Paints',       'metal-paints',       'Anti-corrosive and decorative paints for metal surfaces', 'fa-cog',         '#FFB703', 4, 1),
('Primers & Sealers',  'primers-sealers',    'Surface preparation products',                            'fa-layer-group', '#2BCBBA', 5, 1),
('Texture Paints',     'texture-paints',     'Decorative texture and effect paints',                    'fa-palette',     '#FF9F43', 6, 1),
('Floor Paints',       'floor-paints',       'Heavy-duty paints for floor surfaces',                    'fa-border-all',  '#A29BFE', 7, 1),
('Waterproofing',      'waterproofing',      'Waterproofing solutions for roofs and walls',             'fa-tint',        '#74B9FF', 8, 1),
('Thinners & Solvents','thinners-solvents',  'Paint thinners, removers, and cleaning solvents',        'fa-flask',       '#FD79A8', 9, 1),
('Tools & Accessories','tools-accessories',  'Brushes, rollers, trays, and applicators',               'fa-tools',       '#55EFC4', 10, 1);


-- ============================================================
-- BRANDS
-- ============================================================
INSERT INTO brands (name, slug, description, website, country, is_active, sort_order) VALUES
('Asian Paints',        'asian-paints',        'India\'s largest paint company - premium quality range',   'https://www.asianpaints.com',   'India', 1, 1),
('Berger Paints',       'berger-paints',       'One of India\'s oldest and most trusted paint brands',     'https://www.bergerpaints.com',  'India', 1, 2),
('Nerolac Paints',      'nerolac-paints',      'Kansai Nerolac Paints - health-based paint innovations',   'https://www.nerolac.com',       'India', 1, 3),
('Dulux (AkzoNobel)',   'dulux-akzonobel',     'AkzoNobel\'s premium Dulux range for Indian markets',      'https://www.dulux.in',          'India', 1, 4),
('Indigo Paints',       'indigo-paints',       'Fast-growing challenger brand with innovative products',    'https://www.indigopaints.com',  'India', 1, 5),
('Shalimar Paints',     'shalimar-paints',     'Pioneer paint company with 125+ years of heritage',        'https://www.shalimarpaints.com','India', 1, 6),
('JSW Paints',          'jsw-paints',          'New-age paint brand by the JSW Group',                     'https://www.jswpaints.in',      'India', 1, 7),
('Nippon Paint',        'nippon-paint',        'Japan\'s largest paint manufacturer - global quality',      'https://www.nipponpaint.in',    'India', 1, 8),
('British Paints',      'british-paints',      'Classic British heritage, adapted for Indian climate',      'https://www.britishpaints.in',  'India', 1, 9),
('Snowcem',             'snowcem',             'Specialist in cement-based and masonry paints',             'https://www.snowcem.in',        'India', 1, 10);


-- ============================================================
-- SUPPLIERS
-- ============================================================
INSERT INTO suppliers (name, contact_person, email, phone, gst_number, address_line1, city, state, pincode, country, credit_limit, payment_terms_days, is_active) VALUES
('Asian Paints Direct Supply',  'Rajesh Kumar',  'rajesh@asianpaintssupply.com', '9812345670', '27AADCA1234B1Z5', '12, MIDC Industrial Area', 'Mumbai',     'Maharashtra', '400093', 'India', 500000.00, 30, 1),
('Berger Wholesale Depot',      'Priya Sharma',  'priya@bergerwholesale.com',    '9823456781', '29AAJCB5678C2Z6', '45, Ring Road',             'Bengaluru',  'Karnataka',   '560078', 'India', 300000.00, 30, 1),
('Nerolac Paint Hub',           'Anil Patel',    'anil@nerolachub.com',          '9834567892', '24AANCA9012D3Z7', '78, Industrial Estate',     'Ahmedabad',  'Gujarat',     '380025', 'India', 250000.00, 45, 1),
('Dulux Authorized Distributor','Sunita Reddy',  'sunita@duluxdist.com',         '9845678903', '36AADCA3456E4Z8', '23, MG Road',               'Hyderabad',  'Telangana',   '500001', 'India', 200000.00, 30, 1),
('Indigo Paint Traders',        'Vikram Singh',  'vikram@indigotraders.com',     '9856789014', '07AAACI7890F5Z9', '56, Nehru Place',           'New Delhi',  'Delhi',       '110019', 'India', 150000.00, 45, 1);


-- ============================================================
-- CUSTOMERS
-- ============================================================
INSERT INTO customers (name, customer_type, email, phone, gst_number, address_line1, city, state, pincode, country, credit_limit, is_active) VALUES
('Arun Construction Co.',    'business',    'arun@arunconstruction.in',  '9901234567', '29AAAAA1234A1Z1', '12, Builder\'s Colony',    'Bengaluru', 'Karnataka',   '560001', 'India', 100000.00, 1),
('Priya Interior Designs',   'business',    'priya@priyainteriors.com',  '9912345678', '27BBBBB2345B2Z2', '45, Design Hub',           'Mumbai',    'Maharashtra', '400001', 'India', 75000.00,  1),
('Ravi Painting Services',   'individual',  'ravi.painter@gmail.com',    '9923456789', NULL,               '78, Labour Colony',        'Chennai',   'Tamil Nadu',  '600001', 'India', 25000.00,  1),
('City Hardware Store',      'business',    'info@cityhardware.com',     '9934567890', '24CCCCC3456C3Z3', '23, Market Street',        'Ahmedabad', 'Gujarat',     '380001', 'India', 50000.00,  1),
('Green Home Builders',      'business',    'contact@greenhome.com',     '9945678901', '36DDDDD4567D4Z4', '56, Commercial Complex',   'Hyderabad', 'Telangana',   '500002', 'India', 200000.00, 1),
('Modern Decor Studio',      'business',    'hello@moderndecor.in',      '9956789012', '07EEEEE5678E5Z5', '89, Design Street',        'New Delhi', 'Delhi',       '110001', 'India', 80000.00,  1),
('Walk-in Customer',         'individual',  NULL,                         '0000000000', NULL,               NULL,                       NULL,        NULL,          NULL,     'India', 0.00,      1);


-- ============================================================
-- PRODUCTS  (sample paint products)
-- ============================================================
INSERT INTO products
  (category_id, brand_id, supplier_id, sku, name, slug, paint_type, color_name, color_hex, color_rgb,
   finish, pack_size, cost_price, selling_price, gst_percentage, current_stock,
   minimum_stock, maximum_stock, reorder_quantity, unit, storage_location, is_active, created_by)
VALUES
-- Asian Paints Interior Emulsions
(1, 1, 1, 'AP-INT-001', 'Asian Paints Royale Shyne - Ivory White',     'ap-royale-shyne-ivory-white',
 'Interior Emulsion', 'Ivory White',     '#FFFFF0', '255,255,240', 'Silk',       '4 L',  520.00,  650.00, 18, 45, 5, 100, 20, 'tin',  'Warehouse A - Rack 1', 1, 1),

(1, 1, 1, 'AP-INT-002', 'Asian Paints Royale Shyne - Lavender Mist',   'ap-royale-shyne-lavender-mist',
 'Interior Emulsion', 'Lavender Mist',   '#E6E6FA', '230,230,250', 'Silk',       '4 L',  520.00,  650.00, 18, 30, 5, 100, 20, 'tin',  'Warehouse A - Rack 1', 1, 1),

(1, 1, 1, 'AP-INT-003', 'Asian Paints Tractor Emulsion - Brilliant White', 'ap-tractor-emulsion-brilliant-white',
 'Interior Emulsion', 'Brilliant White', '#FFFFFF', '255,255,255', 'Matte',      '10 L', 680.00,  850.00, 18, 60, 10, 200, 30, 'tin',  'Warehouse A - Rack 2', 1, 1),

(1, 1, 1, 'AP-INT-004', 'Asian Paints Apcolite Emulsion - Cream',       'ap-apcolite-emulsion-cream',
 'Interior Emulsion', 'Cream',           '#FFFDD0', '255,253,208', 'Eggshell',   '4 L',  380.00,  480.00, 18,  8, 5, 80,  15, 'tin',  'Warehouse A - Rack 2', 1, 1),

-- Berger Exterior Paints
(2, 2, 2, 'BP-EXT-001', 'Berger WeatherCoat All Guard - Deep Blue',     'bp-weathercoat-deep-blue',
 'Exterior Emulsion', 'Deep Blue',       '#003153', '0,49,83',     'Semi-Gloss', '10 L', 890.00, 1100.00, 18, 25, 5, 100, 20, 'tin',  'Warehouse A - Rack 3', 1, 1),

(2, 2, 2, 'BP-EXT-002', 'Berger WeatherCoat All Guard - Terracotta',    'bp-weathercoat-terracotta',
 'Exterior Emulsion', 'Terracotta',      '#E2725B', '226,114,91',  'Satin',      '10 L', 890.00, 1100.00, 18,  4, 5, 100, 20, 'tin',  'Warehouse A - Rack 3', 1, 1),

-- Nerolac Primers
(5, 3, 3, 'NR-PRM-001', 'Nerolac Excel Wall Primer',                    'nr-excel-wall-primer',
 'Primer',            'White',           '#F5F5F5', '245,245,245', 'Flat',       '4 L',  310.00,  390.00, 18, 55, 10, 150, 25, 'tin',  'Warehouse B - Shelf 1', 1, 1),

(5, 3, 3, 'NR-PRM-002', 'Nerolac Wood Primer - Grey',                   'nr-wood-primer-grey',
 'Primer',            'Grey',            '#808080', '128,128,128', 'Flat',       '1 L',  120.00,  155.00, 18, 40, 8, 100, 15, 'tin',  'Warehouse B - Shelf 1', 1, 1),

-- Dulux Wood Finishes
(3, 4, 4, 'DX-WD-001',  'Dulux Weathershield Wood Polish - Teak Brown', 'dx-weathershield-wood-teak',
 'Wood Paint',        'Teak Brown',      '#4E2A04', '78,42,4',     'Gloss',      '1 L',  280.00,  360.00, 18, 22, 5, 80,  12, 'tin',  'Warehouse B - Shelf 2', 1, 1),

-- Indigo Paints Texture
(6, 5, 5, 'IP-TX-001',  'Indigo Paints Tile Coat - Slate Grey',         'ip-tile-coat-slate-grey',
 'Texture Paint',     'Slate Grey',      '#708090', '112,128,144', 'Satin',      '4 L',  640.00,  800.00, 18, 18, 5, 60,  10, 'tin',  'Store Front',           1, 1),

(6, 5, 5, 'IP-TX-002',  'Indigo Paints Damp Blocker - White',           'ip-damp-blocker-white',
 'Texture Paint',     'White',           '#FFFFFF', '255,255,255', 'Matte',      '4 L',  720.00,  900.00, 18,  0, 5, 60,  10, 'tin',  'Store Front',           1, 1),

-- Enamel Paints
(4, 1, 1, 'AP-EN-001',  'Asian Paints Apcolite Enamel - Cherry Red',    'ap-apcolite-enamel-cherry-red',
 'Enamel Paint',      'Cherry Red',      '#DC143C', '220,20,60',   'High-Gloss', '1 L',  175.00,  220.00, 18, 35, 8, 100, 15, 'tin',  'Warehouse A - Rack 1', 1, 1),

(4, 1, 1, 'AP-EN-002',  'Asian Paints Apcolite Enamel - Royal Blue',    'ap-apcolite-enamel-royal-blue',
 'Enamel Paint',      'Royal Blue',      '#4169E1', '65,105,225',  'High-Gloss', '1 L',  175.00,  220.00, 18, 15, 8, 100, 15, 'tin',  'Warehouse A - Rack 1', 1, 1),

(4, 2, 2, 'BP-EN-001',  'Berger Luxol Hi-Gloss Enamel - Forest Green',  'bp-luxol-higloss-forest-green',
 'Enamel Paint',      'Forest Green',    '#228B22', '34,139,34',   'High-Gloss', '1 L',  165.00,  210.00, 18, 28, 8, 100, 15, 'tin',  'Warehouse A - Rack 2', 1, 1),

-- Floor Paint
(7, 3, 3, 'NR-FP-001',  'Nerolac Impressions Floor Coat - Stone Grey',  'nr-floor-coat-stone-grey',
 'Floor Paint',       'Stone Grey',      '#928E85', '146,142,133', 'Semi-Gloss', '4 L',  480.00,  600.00, 18, 12, 5, 50,  10, 'tin',  'Warehouse B - Shelf 2', 1, 1);


-- ============================================================
-- SETTINGS  (default application configuration)
-- ============================================================
INSERT INTO settings (setting_key, setting_value, setting_type, category, label, description, is_public) VALUES
-- Company Settings
('company_name',         'PaintPro Solutions',      'string',  'company', 'Company Name',         'Your company or store name',                          1),
('company_tagline',      'Colors That Inspire',     'string',  'company', 'Tagline',              'Company tagline shown on invoices',                   1),
('company_address',      '123 Business Street, City, State - 000000', 'text', 'company', 'Address', 'Full address for invoices', 1),
('company_phone',        '+91 98765 43210',          'string',  'company', 'Phone',                'Primary contact phone',                               1),
('company_email',        'info@paintpro.com',        'string',  'company', 'Email',                'Primary contact email',                               1),
('company_gst',          '22AAAAA0000A1Z5',          'string',  'company', 'GST Number',           'GSTIN for invoice compliance',                        1),
('company_website',      'www.paintpro.com',         'string',  'company', 'Website',              'Company website URL',                                 1),
('currency_symbol',      '₹',                        'string',  'general', 'Currency Symbol',      'Symbol to prepend to all monetary values',            1),
('currency_code',        'INR',                      'string',  'general', 'Currency Code',        'ISO 4217 currency code',                              1),
-- Invoice Settings
('invoice_prefix',       'INV',                      'string',  'invoice', 'Invoice Prefix',       'Prefix for auto-generated invoice numbers',           0),
('po_prefix',            'PO',                       'string',  'invoice', 'PO Prefix',            'Prefix for auto-generated PO numbers',                0),
('invoice_footer_text',  'Thank you for your business!', 'text','invoice', 'Invoice Footer',       'Text shown at bottom of invoices',                    0),
('default_gst_rate',     '18',                       'integer', 'invoice', 'Default GST Rate (%)', 'Default GST rate applied to new products',            0),
('default_payment_terms','30',                       'integer', 'invoice', 'Payment Terms (days)', 'Default credit period for customers',                 0),
-- System Settings
('items_per_page',       '25',                       'integer', 'system',  'Items Per Page',       'Default pagination size',                             0),
('low_stock_threshold',  '10',                       'integer', 'system',  'Low Stock Threshold',  'Global minimum stock level for alerts',               0),
('theme_mode',           'dark',                     'string',  'system',  'Theme Mode',           'Default UI theme: dark or light',                     1),
('date_format',          'DD/MM/YYYY',               'string',  'system',  'Date Format',          'Display format for dates across the app',             1),
('enable_notifications', '1',                        'boolean', 'system',  'Enable Notifications', 'Toggle real-time in-app notifications',               0),
-- AI Settings
('ai_critical_days',     '7',                        'integer', 'ai',      'Critical Days',        'Days remaining to flag as Critical stock alert',      0),
('ai_warning_days',      '14',                       'integer', 'ai',      'Warning Days',         'Days remaining to flag as Warning stock alert',       0),
('reorder_buffer_days',  '5',                        'integer', 'ai',      'Reorder Buffer Days',  'Extra days added when calculating reorder quantity',  0);


-- ============================================================
-- SAMPLE PURCHASE (to demonstrate purchase flow)
-- ============================================================
INSERT INTO purchases
  (supplier_id, created_by, po_number, order_date, received_date,
   subtotal, gst_amount, grand_total, paid_amount, status, payment_status)
VALUES
  (1, 1, 'PO-2026-00001', '2026-07-01', '2026-07-03',
   18560.00, 3340.80, 21900.80, 21900.80, 'received', 'paid');

INSERT INTO purchase_items
  (purchase_id, product_id, quantity_ordered, quantity_received, unit_cost,
   gst_percentage, gst_amount, line_total)
VALUES
  (1, 1, 20, 20, 520.00, 18, 1872.00, 14072.00),
  (1, 2, 15, 15, 520.00, 18, 1404.00, 10764.00);


-- ============================================================
-- SAMPLE SALES (to populate dashboard charts)
-- ============================================================
INSERT INTO sales
  (customer_id, created_by, invoice_number, invoice_date,
   customer_name, subtotal, gst_amount, grand_total, paid_amount, balance_due,
   payment_method, payment_status, status)
VALUES
  (1, 1, 'INV-2026-00001', '2026-07-05',
   'Arun Construction Co.', 6780.00, 1220.40, 8000.40, 8000.40, 0.00,
   'bank_transfer', 'paid', 'delivered'),

  (2, 1, 'INV-2026-00002', '2026-07-06',
   'Priya Interior Designs', 4237.00,  762.66, 4999.66, 2500.00, 2499.66,
   'upi', 'partial', 'delivered'),

  (3, 2, 'INV-2026-00003', '2026-07-07',
   'Ravi Painting Services', 2033.00,  365.94, 2398.94, 2398.94, 0.00,
   'cash', 'paid', 'delivered'),

  (7, 2, 'INV-2026-00004', CURDATE(),
   'Walk-in Customer',       1100.00,  198.00, 1298.00, 1298.00, 0.00,
   'cash', 'paid', 'delivered');

INSERT INTO sale_items
  (sale_id, product_id, product_name, product_sku, color_name, pack_size,
   quantity, unit_price, cost_price, gst_percentage, gst_amount, line_total)
VALUES
  (1, 3, 'Asian Paints Tractor Emulsion - Brilliant White', 'AP-INT-003', 'Brilliant White', '10 L',
   8, 850.00, 680.00, 18, 1224.00, 8024.00),

  (2, 10, 'Indigo Paints Tile Coat - Slate Grey', 'IP-TX-001', 'Slate Grey', '4 L',
   5, 800.00, 640.00, 18, 720.00, 4720.00),

  (3, 12, 'Asian Paints Apcolite Enamel - Cherry Red', 'AP-EN-001', 'Cherry Red', '1 L',
   9, 220.00, 175.00, 18, 356.40, 2336.40),

  (4, 7, 'Nerolac Excel Wall Primer', 'NR-PRM-001', 'White', '4 L',
   3, 390.00, 310.00, 18, 210.60, 1380.60);


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- End of Seed Data
-- ============================================================
