"""
PaintPro Inventory Management System
=====================================
Input Validators  |  utils/validators.py

All validators return (is_valid: bool, error_message: str).
Empty error message means validation passed.
"""

import re
from typing import Optional
from datetime import date


# ─── Auth Validators ──────────────────────────────────────────────────────────

def validate_email(email: str) -> tuple[bool, str]:
    """Validate an email address format."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not email or not email.strip():
        return False, "Email is required."
    if not re.match(pattern, email.strip()):
        return False, "Enter a valid email address."
    return True, ""


def validate_password(password: str, min_length: int = 8) -> tuple[bool, str]:
    """
    Enforce password policy:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password:
        return False, "Password is required."
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate Indian phone number (10 digits, optionally +91 prefix)."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    cleaned = re.sub(r'[\s\-\(\)]', '', phone.strip())
    if cleaned.startswith('+91'):
        cleaned = cleaned[3:]
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not re.match(r'^[6-9]\d{9}$', cleaned):
        return False, "Enter a valid 10-digit Indian mobile number."
    return True, ""


def validate_name(name: str, field: str = "Name", min_len: int = 2, max_len: int = 200) -> tuple[bool, str]:
    """Validate a generic name field."""
    if not name or not name.strip():
        return False, f"{field} is required."
    if len(name.strip()) < min_len:
        return False, f"{field} must be at least {min_len} characters."
    if len(name.strip()) > max_len:
        return False, f"{field} cannot exceed {max_len} characters."
    return True, ""


# ─── Product Validators ───────────────────────────────────────────────────────

def validate_sku(sku: str) -> tuple[bool, str]:
    """Validate a product SKU - alphanumeric, hyphens, underscores."""
    if not sku or not sku.strip():
        return False, "SKU is required."
    if not re.match(r'^[A-Za-z0-9\-_]{2,50}$', sku.strip()):
        return False, "SKU must be 2–50 chars: letters, digits, hyphens, underscores only."
    return True, ""


def validate_price(value: float | str, field: str = "Price") -> tuple[bool, str]:
    """Validate a monetary value is a non-negative number."""
    try:
        v = float(value)
        if v < 0:
            return False, f"{field} cannot be negative."
    except (TypeError, ValueError):
        return False, f"{field} must be a valid number."
    return True, ""


def validate_stock(value: float | str, field: str = "Stock") -> tuple[bool, str]:
    """Validate a stock quantity is a non-negative number."""
    try:
        v = float(value)
        if v < 0:
            return False, f"{field} cannot be negative."
    except (TypeError, ValueError):
        return False, f"{field} must be a valid number."
    return True, ""


def validate_hex_color(hex_color: str) -> tuple[bool, str]:
    """Validate a 3 or 6 digit hex color code (with or without #)."""
    if not hex_color:
        return True, ""  # Optional field
    pattern = r'^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not re.match(pattern, hex_color.strip()):
        return False, "Enter a valid HEX color code (e.g. #FF5733 or #F73)."
    return True, ""


def validate_gst_number(gst: str) -> tuple[bool, str]:
    """Validate a 15-character Indian GSTIN."""
    if not gst or not gst.strip():
        return True, ""  # Optional field
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, gst.strip().upper()):
        return False, "Enter a valid 15-character GSTIN (e.g. 22AAAAA0000A1Z5)."
    return True, ""


def validate_pincode(pincode: str) -> tuple[bool, str]:
    """Validate a 6-digit Indian PIN code."""
    if not pincode or not pincode.strip():
        return True, ""  # Optional
    if not re.match(r'^\d{6}$', pincode.strip()):
        return False, "PIN code must be exactly 6 digits."
    return True, ""


def validate_date_range(
    start: Optional[date],
    end: Optional[date],
    field: str = "Date range",
) -> tuple[bool, str]:
    """Validate that start date is not after end date."""
    if start and end and start > end:
        return False, f"{field}: start date must be before end date."
    return True, ""


def validate_required(value, field: str) -> tuple[bool, str]:
    """Generic non-empty validator."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field} is required."
    return True, ""


def validate_positive_integer(value, field: str = "Value") -> tuple[bool, str]:
    """Validate that a value is a positive integer."""
    try:
        v = int(value)
        if v <= 0:
            return False, f"{field} must be greater than zero."
    except (TypeError, ValueError):
        return False, f"{field} must be a whole number."
    return True, ""


def validate_percentage(value: float | str, field: str = "Percentage") -> tuple[bool, str]:
    """Validate a percentage is between 0 and 100."""
    try:
        v = float(value)
        if not (0 <= v <= 100):
            return False, f"{field} must be between 0 and 100."
    except (TypeError, ValueError):
        return False, f"{field} must be a valid number."
    return True, ""


# ─── Batch Validator ──────────────────────────────────────────────────────────

def run_validations(rules: list[tuple[bool, str]]) -> tuple[bool, list[str]]:
    """
    Run multiple (is_valid, error) pairs at once.

    Args:
        rules: List of (is_valid, error_message) tuples from individual validators.

    Returns:
        (all_valid: bool, errors: list[str])
    """
    errors = [msg for ok, msg in rules if not ok and msg]
    return len(errors) == 0, errors
