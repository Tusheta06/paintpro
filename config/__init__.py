"""
PaintPro Inventory Management System
=====================================
Config Package Initializer

Re-exports commonly used config objects for convenient imports:
    from config import db_config, app_config, ROLES
"""

from config.settings import (
    db_config,
    app_config,
    company_config,
    upload_config,
    theme_config,
)
from config.constants import (
    ROLES,
    ROLE_PERMISSIONS,
    PAINT_TYPES,
    PAINT_FINISHES,
    PACK_SIZES,
    DEFAULT_BRANDS,
    GST_RATES,
    STOCK_STATUS,
    STOCK_STATUS_COLORS,
    PAYMENT_STATUS,
    PAYMENT_STATUS_COLORS,
    ORDER_STATUS,
    ORDER_STATUS_COLORS,
    STOCK_LOG_TYPES,
    NOTIFICATION_TYPES,
    NOTIFICATION_ICONS,
    DATE_FORMAT,
    DATETIME_FORMAT,
    DB_DATE_FORMAT,
    DB_DATETIME_FORMAT,
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
    PAGE_SIZES,
    EXPORT_FORMATS,
    STORAGE_LOCATIONS,
    AI_CRITICAL_DAYS,
    AI_WARNING_DAYS,
    AI_SAFE_DAYS,
    REORDER_BUFFER_DAYS,
)

__all__ = [
    "db_config",
    "app_config",
    "company_config",
    "upload_config",
    "theme_config",
    "ROLES",
    "ROLE_PERMISSIONS",
    "PAINT_TYPES",
    "PAINT_FINISHES",
    "PACK_SIZES",
    "DEFAULT_BRANDS",
    "GST_RATES",
    "STOCK_STATUS",
    "STOCK_STATUS_COLORS",
    "PAYMENT_STATUS",
    "PAYMENT_STATUS_COLORS",
    "ORDER_STATUS",
    "ORDER_STATUS_COLORS",
    "STOCK_LOG_TYPES",
    "NOTIFICATION_TYPES",
    "NOTIFICATION_ICONS",
    "DATE_FORMAT",
    "DATETIME_FORMAT",
    "DB_DATE_FORMAT",
    "DB_DATETIME_FORMAT",
    "CURRENCY_SYMBOL",
    "CURRENCY_CODE",
    "PAGE_SIZES",
    "EXPORT_FORMATS",
    "STORAGE_LOCATIONS",
    "AI_CRITICAL_DAYS",
    "AI_WARNING_DAYS",
    "AI_SAFE_DAYS",
    "REORDER_BUFFER_DAYS",
]
