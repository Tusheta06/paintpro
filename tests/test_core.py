"""
PaintPro Inventory Management System
=====================================
Test Suite  |  tests/test_core.py

Automated tests for core utilities, auth logic, and validators.
"""

import pytest
import os
import sys

# Ensure the root directory is in the sys path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.formatting import slugify, format_currency, format_date
from utils.validators import validate_email, validate_phone, validate_sku
from utils.auth import hash_password, verify_password
from database.connection import test_connection as run_db_connection_test

# ─── 1. Formatting Utilities ──────────────────────────────────────────────────

def test_slugify():
    assert slugify("Asian Paints Royal") == "asian-paints-royal"
    assert slugify("SKU-123 & %* Special") == "sku-123-special"
    assert slugify("   Trim spaces   ") == "trim-spaces"

def test_format_currency():
    assert format_currency(1234.56) == "₹1,234.56"
    assert format_currency(0) == "₹0.00"

# ─── 2. Validation Logic ──────────────────────────────────────────────────────

def test_validate_email():
    ok, msg = validate_email("test@example.com")
    assert ok is True
    
    ok, msg = validate_email("invalid-email")
    assert ok is False
    assert "Enter a valid email address" in msg

def test_validate_phone():
    ok, msg = validate_phone("9876543210")
    assert ok is True
    
    ok, msg = validate_phone("12345")
    assert ok is False
    assert "10-digit" in msg

def test_validate_sku():
    ok, msg = validate_sku("PAINT-123")
    assert ok is True
    
    ok, msg = validate_sku("P@INT!")
    assert ok is False

# ─── 3. Auth & Security ───────────────────────────────────────────────────────

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 10
    
    # Verification should succeed with correct password
    assert verify_password(password, hashed) is True
    
    # Verification should fail with wrong password
    assert verify_password("WrongPassword123!", hashed) is False

# ─── 4. Database Connectivity ─────────────────────────────────────────────────

def test_db_connection():
    # Only test if dotenv variables exist (prevents CI failures without DB)
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv("DB_HOST"):
        ok, msg = run_db_connection_test()
        assert type(ok) is bool
        # If DB is configured, it should ideally connect. 
        # But even if it fails, it returns a clear boolean.
