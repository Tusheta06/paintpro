"""
PaintPro Inventory Management System
=====================================
Utils Package Initializer

Re-exports common utilities for convenient single-import usage:
    from utils import format_currency, log_activity, validate_email
"""

from utils.auth import (
    login_user,
    logout_user,
    register_user,
    is_authenticated,
    get_current_user,
    has_permission,
    require_auth,
    require_permission,
    log_activity,
    change_password,
    update_profile,
    generate_reset_token,
    reset_password_with_token,
)

from utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
    format_date,
    format_datetime,
    timeago,
    truncate,
    title_case,
    slugify,
    format_stock,
    get_stock_status,
    get_stock_badge_html,
    get_payment_badge_html,
)

from utils.validators import (
    validate_email,
    validate_password,
    validate_phone,
    validate_name,
    validate_sku,
    validate_price,
    validate_stock,
    validate_hex_color,
    validate_gst_number,
    validate_pincode,
    validate_required,
    validate_percentage,
    validate_positive_integer,
    run_validations,
)

__all__ = [
    # Auth
    "login_user", "logout_user", "register_user",
    "is_authenticated", "get_current_user", "has_permission",
    "require_auth", "require_permission", "log_activity",
    "change_password", "update_profile",
    "generate_reset_token", "reset_password_with_token",
    # Formatting
    "format_currency", "format_number", "format_percentage",
    "format_date", "format_datetime", "timeago",
    "truncate", "title_case", "slugify",
    "format_stock", "get_stock_status",
    "get_stock_badge_html", "get_payment_badge_html",
    # Validators
    "validate_email", "validate_password", "validate_phone",
    "validate_name", "validate_sku", "validate_price",
    "validate_stock", "validate_hex_color", "validate_gst_number",
    "validate_pincode", "validate_required", "validate_percentage",
    "validate_positive_integer", "run_validations",
]
