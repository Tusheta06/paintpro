"""
PaintPro Inventory Management System
=====================================
Application Constants

Defines all domain-level constants used across modules:
roles, paint types, finish types, GST rates, status enums, etc.
"""

# ─── User Roles ───────────────────────────────────────────────────────────────
ROLES = {
    "admin": "Admin",
    "manager": "Manager",
    "employee": "Employee",
}

USER_ROLES_LIST = ["admin", "manager", "employee"]

# ─── Customer Types ───────────────────────────────────────────────────────────
CUSTOMER_TYPES = ["individual", "business"]

CUSTOMER_TYPE_LABELS = {
    "individual": "Individual / Retail",
    "business": "Business / B2B",
}
ROLE_PERMISSIONS = {
    "admin": [
        "dashboard", "inventory", "categories", "brands", "suppliers",
        "customers", "purchases", "sales", "stock_management", "reports",
        "analytics", "user_management", "notifications", "export_center",
        "settings", "profile",
    ],
    "manager": [
        "dashboard", "inventory", "categories", "brands", "suppliers",
        "customers", "purchases", "sales", "stock_management", "reports",
        "analytics", "notifications", "export_center", "profile",
    ],
    "employee": [
        "dashboard", "inventory", "customers", "sales", "stock_management",
        "notifications", "profile",
    ],
}

# ─── Paint Types ──────────────────────────────────────────────────────────────
PAINT_TYPES = [
    "Interior Emulsion",
    "Exterior Emulsion",
    "Enamel Paint",
    "Distemper",
    "Primer",
    "Varnish",
    "Wood Paint",
    "Anti-Corrosive Paint",
    "Cement Paint",
    "Texture Paint",
    "Epoxy Paint",
    "Acrylic Paint",
    "Oil-Based Paint",
    "Water-Based Paint",
    "Metallic Paint",
    "Roof Paint",
    "Floor Paint",
    "Other",
]

# ─── Paint Finishes ───────────────────────────────────────────────────────────
PAINT_FINISHES = [
    "Matte",
    "Flat",
    "Eggshell",
    "Satin",
    "Semi-Gloss",
    "Gloss",
    "High-Gloss",
    "Silk",
    "Sheen",
    "Suede",
]

# ─── Pack Sizes ───────────────────────────────────────────────────────────────
PACK_SIZES = [
    "100 ml",
    "200 ml",
    "500 ml",
    "1 L",
    "1.8 L",
    "2 L",
    "3.6 L",
    "4 L",
    "10 L",
    "15 L",
    "20 L",
    "25 L",
    "50 L",
    "Custom",
]

# ─── Default Brands ───────────────────────────────────────────────────────────
DEFAULT_BRANDS = [
    "Asian Paints",
    "Berger Paints",
    "Nerolac Paints",
    "Dulux (AkzoNobel)",
    "Indigo Paints",
    "Shalimar Paints",
    "JSW Paints",
    "Nippon Paint",
    "British Paints",
    "Snowcem",
]

# ─── GST Rates ────────────────────────────────────────────────────────────────
GST_RATES = [0, 5, 12, 18, 28]  # Percentage values

# ─── Stock Status ─────────────────────────────────────────────────────────────
STOCK_STATUS = {
    "in_stock": "In Stock",
    "low_stock": "Low Stock",
    "out_of_stock": "Out of Stock",
    "discontinued": "Discontinued",
    "damaged": "Damaged",
}

STOCK_STATUS_COLORS = {
    "in_stock": "#00D4AA",
    "low_stock": "#FFB703",
    "out_of_stock": "#FF4757",
    "discontinued": "#8B92A9",
    "damaged": "#FF6B6B",
}

# ─── Payment Status ───────────────────────────────────────────────────────────
PAYMENT_STATUS = {
    "paid": "Paid",
    "unpaid": "Unpaid",
    "partial": "Partially Paid",
    "overdue": "Overdue",
    "cancelled": "Cancelled",
    "refunded": "Refunded",
}

PAYMENT_STATUS_COLORS = {
    "paid": "#00D4AA",
    "unpaid": "#FF4757",
    "partial": "#FFB703",
    "overdue": "#FF6B6B",
    "cancelled": "#8B92A9",
    "refunded": "#6C63FF",
}

# ─── Order Status ─────────────────────────────────────────────────────────────
ORDER_STATUS = {
    "pending": "Pending",
    "processing": "Processing",
    "completed": "Completed",
    "cancelled": "Cancelled",
    "returned": "Returned",
}

ORDER_STATUS_COLORS = {
    "pending": "#FFB703",
    "processing": "#6C63FF",
    "completed": "#00D4AA",
    "cancelled": "#FF4757",
    "returned": "#FF6B6B",
}

# ─── Stock Log Types ──────────────────────────────────────────────────────────
STOCK_LOG_TYPES = {
    "purchase": "Purchase",
    "sale": "Sale",
    "adjustment": "Adjustment",
    "return_in": "Return (Received)",
    "return_out": "Return (Sent)",
    "damaged": "Damaged",
    "opening": "Opening Stock",
    "transfer": "Transfer",
}

STOCK_ADJUSTMENT_REASONS = [
    "Physical Count Correction",
    "Damaged / Expired",
    "Opening Stock Entry",
    "Transfer Between Warehouses",
    "Return from Customer",
    "Return to Supplier",
    "Theft / Shrinkage",
    "Manufacturing / Mixing",
    "Other",
]

# ─── Sale Status ──────────────────────────────────────────────────────────────
SALE_STATUSES = ["draft", "confirmed", "shipped", "delivered", "cancelled", "returned"]
SALE_PAYMENT_STATUSES = ["paid", "unpaid", "partial", "overdue", "cancelled", "refunded"]
SALE_PAYMENT_METHODS = ["cash", "card", "upi", "bank_transfer", "cheque", "credit"]

# ─── Purchase Status ──────────────────────────────────────────────────────────
PURCHASE_STATUSES = ["draft", "ordered", "partial", "received", "cancelled"]
PURCHASE_PAYMENT_STATUSES = ["unpaid", "partial", "paid"]

# ─── Indian States ────────────────────────────────────────────────────────────
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry",
]
# ─── Notification Types ───────────────────────────────────────────────────────
NOTIFICATION_TYPES = {
    "low_stock": "Low Stock Alert",
    "out_of_stock": "Out of Stock",
    "new_sale": "New Sale",
    "new_purchase": "New Purchase",
    "invoice_generated": "Invoice Generated",
    "new_user": "New User Registered",
    "payment_due": "Payment Due",
    "system": "System Notification",
}

NOTIFICATION_ICONS = {
    "low_stock": "⚠️",
    "out_of_stock": "🚨",
    "new_sale": "💰",
    "new_purchase": "🛒",
    "invoice_generated": "📄",
    "new_user": "👤",
    "payment_due": "💳",
    "system": "🔔",
}

# ─── Date Formats ─────────────────────────────────────────────────────────────
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DB_DATE_FORMAT = "%Y-%m-%d"
DB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ─── Currency ─────────────────────────────────────────────────────────────────
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE = "INR"

# ─── Pagination ───────────────────────────────────────────────────────────────
PAGE_SIZES = [10, 25, 50, 100]

# ─── Export Formats ───────────────────────────────────────────────────────────
EXPORT_FORMATS = ["CSV", "Excel", "PDF"]

# ─── Storage Locations ────────────────────────────────────────────────────────
STORAGE_LOCATIONS = [
    "Warehouse A - Rack 1",
    "Warehouse A - Rack 2",
    "Warehouse A - Rack 3",
    "Warehouse B - Shelf 1",
    "Warehouse B - Shelf 2",
    "Store Front",
    "Cold Storage",
    "Overflow Storage",
    "Custom",
]

# ─── AI Prediction Thresholds ─────────────────────────────────────────────────
AI_CRITICAL_DAYS = 7        # < 7 days → critical
AI_WARNING_DAYS = 14        # 7–14 days → warning
AI_SAFE_DAYS = 30           # > 30 days → safe
REORDER_BUFFER_DAYS = 5     # Extra buffer when calculating reorder quantity
