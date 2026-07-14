"""
PaintPro Inventory Management System
=====================================
Database Package Initializer

Re-exports the most commonly used database functions so modules
can do:
    from database import execute_query, execute_write, execute_one
"""

from database.connection import (
    get_connection,
    execute_query,
    execute_one,
    execute_write,
    execute_many,
    execute_transaction,
    fetch_scalar,
    test_connection,
)

__all__ = [
    "get_connection",
    "execute_query",
    "execute_one",
    "execute_write",
    "execute_many",
    "execute_transaction",
    "fetch_scalar",
    "test_connection",
]
