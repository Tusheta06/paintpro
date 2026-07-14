"""
PaintPro Inventory Management System
=====================================
Formatting Utilities  |  utils/formatting.py

Currency, date, number, and text formatting helpers
used consistently across all pages and reports.
"""

from datetime import datetime, date
from typing import Optional

from config.constants import (
    CURRENCY_SYMBOL,
    DATE_FORMAT,
    DATETIME_FORMAT,
    DB_DATE_FORMAT,
    DB_DATETIME_FORMAT,
)


# ─── Currency ────────────────────────────────────────────────────────────────

def format_currency(value: float | int | None, symbol: str = CURRENCY_SYMBOL) -> str:
    """Format a number as Indian currency (e.g. ₹1,23,456.78)."""
    if value is None:
        return f"{symbol}0.00"
    try:
        value = float(value)
        # Indian numbering: last 3 digits, then groups of 2
        abs_val = abs(value)
        str_val = f"{abs_val:.2f}"
        int_part, dec_part = str_val.split(".")
        # Apply Indian grouping
        if len(int_part) > 3:
            last3 = int_part[-3:]
            rest  = int_part[:-3]
            groups = []
            while len(rest) > 2:
                groups.append(rest[-2:])
                rest = rest[:-2]
            if rest:
                groups.append(rest)
            int_part = ",".join(reversed(groups)) + "," + last3
        formatted = f"{symbol}{int_part}.{dec_part}"
        return f"-{formatted}" if value < 0 else formatted
    except (TypeError, ValueError):
        return f"{symbol}0.00"


def format_number(value: float | int | None, decimals: int = 2) -> str:
    """Format a plain number with comma separators."""
    if value is None:
        return "0"
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "0"


def format_percentage(value: float | None, decimals: int = 1) -> str:
    """Format a percentage value (e.g. 18.0%)."""
    if value is None:
        return "0%"
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return "0%"


# ─── Dates ───────────────────────────────────────────────────────────────────

def format_date(value: date | datetime | str | None) -> str:
    """Convert any date value to DD/MM/YYYY display format."""
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.strftime(DATE_FORMAT)
    if isinstance(value, date):
        return value.strftime(DATE_FORMAT)
    if isinstance(value, str):
        for fmt in (DB_DATE_FORMAT, DB_DATETIME_FORMAT, DATE_FORMAT, DATETIME_FORMAT):
            try:
                return datetime.strptime(value, fmt).strftime(DATE_FORMAT)
            except ValueError:
                continue
    return str(value)


def format_datetime(value: datetime | str | None) -> str:
    """Convert any datetime value to DD/MM/YYYY HH:MM:SS display format."""
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.strftime(DATETIME_FORMAT)
    if isinstance(value, str):
        for fmt in (DB_DATETIME_FORMAT, DATETIME_FORMAT, DB_DATE_FORMAT):
            try:
                return datetime.strptime(value, fmt).strftime(DATETIME_FORMAT)
            except ValueError:
                continue
    return str(value)

def timeago(value) -> str:
    """Return a human-readable relative time."""

    if value is None:
        return "Unknown"

    # String from database
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, DB_DATETIME_FORMAT)
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return str(value)

    # If it's a date object (invoice_date), convert it to datetime
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, datetime.min.time())

    now = datetime.now()
    delta = now - value
    secs = int(delta.total_seconds())

    if secs < 60:
        return "just now"
    elif secs < 3600:
        m = secs // 60
        return f"{m} minute{'s' if m > 1 else ''} ago"
    elif secs < 86400:
        h = secs // 3600
        return f"{h} hour{'s' if h > 1 else ''} ago"
    elif secs < 604800:
        d = secs // 86400
        return f"{d} day{'s' if d > 1 else ''} ago"
    elif secs < 2592000:
        w = secs // 604800
        return f"{w} week{'s' if w > 1 else ''} ago"
    else:
        return format_date(value)
# def timeago(value: datetime | str | None) -> str:
#     """Return a human-readable relative time (e.g. '3 hours ago')."""
#     if value is None:
#         return "Unknown"
#     if isinstance(value, str):
#         try:
#             value = datetime.strptime(value, DB_DATETIME_FORMAT)
#         except ValueError:
#             return str(value)

#     now   = datetime.now()
#     delta = now - value
#     secs  = int(delta.total_seconds())

#     if secs < 60:
#         return "just now"
#     elif secs < 3600:
#         m = secs // 60
#         return f"{m} minute{'s' if m > 1 else ''} ago"
#     elif secs < 86400:
#         h = secs // 3600
#         return f"{h} hour{'s' if h > 1 else ''} ago"
#     elif secs < 604800:
#         d = secs // 86400
#         return f"{d} day{'s' if d > 1 else ''} ago"
#     elif secs < 2592000:
#         w = secs // 604800
#         return f"{w} week{'s' if w > 1 else ''} ago"
#     else:
#         return format_date(value)


# ─── Text ─────────────────────────────────────────────────────────────────────

def truncate(text: str, max_length: int = 50, suffix: str = "…") -> str:
    """Truncate long text with a suffix."""
    if not text:
        return ""
    return text if len(text) <= max_length else text[:max_length].rstrip() + suffix


def title_case(text: str) -> str:
    """Convert snake_case or any string to Title Case."""
    return text.replace("_", " ").title() if text else ""


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# ─── Stock / Status ───────────────────────────────────────────────────────────

def format_stock(value: float | None, unit: str = "units") -> str:
    """Format stock quantity with unit label."""
    if value is None:
        return "0"
    v = float(value)
    if v == int(v):
        return f"{int(v):,} {unit}"
    return f"{v:,.2f} {unit}"


def get_stock_status(current: float, minimum: float) -> str:
    """Return stock status key based on levels."""
    if current <= 0:
        return "out_of_stock"
    if current <= minimum:
        return "low_stock"
    return "in_stock"


def get_stock_badge_html(current: float, minimum: float) -> str:
    """Return an HTML badge for inline stock status display."""
    status = get_stock_status(current, minimum)
    colors = {
        "in_stock":    ("#00D4AA", "#0a2a25"),
        "low_stock":   ("#FFB703", "#2a2200"),
        "out_of_stock":("#FF4757", "#2a0a0d"),
    }
    labels = {
        "in_stock":    "In Stock",
        "low_stock":   "Low Stock",
        "out_of_stock":"Out of Stock",
    }
    bg, fg = colors[status]
    label  = labels[status]
    return (
        f'<span style="background:{bg}22;color:{bg};border:1px solid {bg}44;'
        f'padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;">'
        f'{label}</span>'
    )


def get_payment_badge_html(status: str) -> str:
    """Return an HTML badge for payment status."""
    from config.constants import PAYMENT_STATUS_COLORS, PAYMENT_STATUS
    color = PAYMENT_STATUS_COLORS.get(status, "#8B92A9")
    label = PAYMENT_STATUS.get(status, status.title())
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
        f'padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;">'
        f'{label}</span>'
    )
