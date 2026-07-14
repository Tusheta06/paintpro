"""
PaintPro Inventory Management System
=====================================
Configuration Settings Module

Centralizes all application-wide settings, loaded from
environment variables with sensible production defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """MySQL database connection configuration."""

    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", "3306"))
    NAME: str = os.getenv("DB_NAME", "paintpro_db")
    USER: str = os.getenv("DB_USER", "root")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Connection pool settings
    POOL_NAME: str = "paintpro_pool"
    POOL_SIZE: int = 5
    CONNECTION_TIMEOUT: int = 30
    AUTOCOMMIT: bool = False
    CHARSET: str = "utf8mb4"
    COLLATION: str = "utf8mb4_unicode_ci"


class AppConfig:
    """Core application configuration."""

    NAME: str = os.getenv("APP_NAME", "PaintPro IMS")
    VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "paintpro-secret-change-me")

    # Session settings
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))

    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "25"))


class CompanyConfig:
    """Company information used in invoices and reports."""

    NAME: str = os.getenv("COMPANY_NAME", "PaintPro Solutions")
    ADDRESS: str = os.getenv("COMPANY_ADDRESS", "123 Business Street, City")
    PHONE: str = os.getenv("COMPANY_PHONE", "+91 98765 43210")
    EMAIL: str = os.getenv("COMPANY_EMAIL", "info@paintpro.com")
    GST: str = os.getenv("COMPANY_GST", "22AAAAA0000A1Z5")
    WEBSITE: str = os.getenv("COMPANY_WEBSITE", "www.paintpro.com")


class UploadConfig:
    """File upload configuration."""

    MAX_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "5"))
    ALLOWED_TYPES: list = os.getenv(
        "ALLOWED_IMAGE_TYPES", "jpg,jpeg,png,webp"
    ).split(",")
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "assets/images")
    PRODUCTS_FOLDER: str = "assets/images/products"
    REPORTS_FOLDER: str = "reports"


class ThemeConfig:
    """UI theme and branding configuration."""

    PRIMARY_COLOR: str = "#6C63FF"
    SECONDARY_COLOR: str = "#FF6B6B"
    SUCCESS_COLOR: str = "#00D4AA"
    WARNING_COLOR: str = "#FFB703"
    DANGER_COLOR: str = "#FF4757"
    INFO_COLOR: str = "#2BCBBA"

    DARK_BG: str = "#0F1117"
    DARK_SECONDARY_BG: str = "#1A1D27"
    DARK_CARD_BG: str = "#1E2130"
    DARK_BORDER: str = "#2D3250"
    DARK_TEXT: str = "#FFFFFF"
    DARK_MUTED_TEXT: str = "#8B92A9"

    LIGHT_BG: str = "#F8F9FC"
    LIGHT_SECONDARY_BG: str = "#FFFFFF"
    LIGHT_CARD_BG: str = "#FFFFFF"
    LIGHT_BORDER: str = "#E2E8F0"
    LIGHT_TEXT: str = "#1A202C"
    LIGHT_MUTED_TEXT: str = "#718096"

    FONT_PRIMARY: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    BORDER_RADIUS: str = "12px"
    BOX_SHADOW: str = "0 4px 20px rgba(0,0,0,0.15)"


# Expose named config instances
db_config = DatabaseConfig()
app_config = AppConfig()
company_config = CompanyConfig()
upload_config = UploadConfig()
theme_config = ThemeConfig()
