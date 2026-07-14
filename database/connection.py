"""
PaintPro Inventory Management System
=====================================
Database Connection Layer  |  database/connection.py

Provides:
  - get_connection()         → single raw connection
  - execute_query()          → SELECT returning list[dict]
  - execute_one()            → SELECT returning dict | None
  - execute_write()          → INSERT / UPDATE / DELETE returning affected rows / last_insert_id
  - execute_many()           → executemany for bulk operations
  - test_connection()        → health-check boolean

All queries use parameterized placeholders (%s) to prevent SQL injection.
Connections are NOT pooled at this layer - Streamlit's session model
means we open/close per-request; pooling is handled by MySQL itself.
"""

import sys
from pathlib import Path
from typing import Any

import mysql.connector
from mysql.connector import Error as MySQLError

# Allow imports from project root when running standalone
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import db_config


# ─── Connection Factory ────────────────────────────────────────────────────────

def get_connection() -> mysql.connector.MySQLConnection:
    """
    Open and return a raw MySQL connection.

    The caller is responsible for closing it (use with a try/finally block
    or the context manager pattern).

    Raises:
        mysql.connector.Error if the connection cannot be established.
    """
    return mysql.connector.connect(
        host=db_config.HOST,
        port=db_config.PORT,
        database=db_config.NAME,
        user=db_config.USER,
        password=db_config.PASSWORD,
        charset=db_config.CHARSET,
        collation=db_config.COLLATION,
        autocommit=False,
        connection_timeout=db_config.CONNECTION_TIMEOUT,
        use_unicode=True,
        ssl_verify_cert=False,  # <--- CRITICAL FOR AIVEN CLOUD
    )


# ─── Query Helpers ─────────────────────────────────────────────────────────────

def execute_query(
    sql: str,
    params: tuple | list | None = None,
    fetch_all: bool = True,
) -> list[dict[str, Any]]:
    """
    Execute a SELECT statement and return results as a list of dicts.

    Args:
        sql:       Parameterized SQL string with %s placeholders.
        params:    Tuple or list of bound values.
        fetch_all: If False, fetches only the first row (returns list with 0 or 1 item).

    Returns:
        List of row dicts (column_name → value).

    Raises:
        mysql.connector.Error on database errors.
    """
    conn = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall() if fetch_all else [cursor.fetchone()] if cursor.fetchone() else []
        return rows
    except MySQLError as exc:
        raise exc
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_one(
    sql: str,
    params: tuple | list | None = None,
) -> dict[str, Any] | None:
    """
    Execute a SELECT statement and return a single row as a dict, or None.

    Convenience wrapper around execute_query for single-row lookups.
    """
    conn = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(sql, params or ())
        return cursor.fetchone()
    except MySQLError as exc:
        raise exc
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_write(
    sql: str,
    params: tuple | list | None = None,
    return_last_id: bool = False,
) -> int:
    """
    Execute an INSERT, UPDATE, or DELETE statement.

    Args:
        sql:            Parameterized SQL string.
        params:         Bound parameter values.
        return_last_id: If True, returns lastrowid (for INSERT).
                        If False, returns rowcount (affected rows).

    Returns:
        lastrowid or rowcount as an integer.

    Raises:
        mysql.connector.Error on database errors (triggers rollback).
    """
    conn = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid if return_last_id else cursor.rowcount
    except MySQLError as exc:
        if conn:
            conn.rollback()
        raise exc
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_many(
    sql: str,
    params_list: list[tuple | list],
) -> int:
    """
    Execute a parameterized statement for each item in params_list (bulk ops).

    Args:
        sql:         Parameterized SQL string.
        params_list: List of parameter tuples.

    Returns:
        Total rowcount.
    """
    conn = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()
        return cursor.rowcount
    except MySQLError as exc:
        if conn:
            conn.rollback()
        raise exc
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_transaction(
    statements: list[tuple[str, tuple | list | None]],
) -> bool:
    """
    Execute multiple SQL statements as a single atomic transaction.

    Args:
        statements: List of (sql, params) tuples to execute in order.

    Returns:
        True if all statements committed successfully.

    Raises:
        mysql.connector.Error - triggers full rollback on any failure.
    """
    conn = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        for sql, params in statements:
            cursor.execute(sql, params or ())
        conn.commit()
        return True
    except MySQLError as exc:
        if conn:
            conn.rollback()
        raise exc
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ─── Health Check ─────────────────────────────────────────────────────────────

def test_connection() -> tuple[bool, str]:
    """
    Verify database connectivity.

    Returns:
        (True, "OK") on success.
        (False, error_message) on failure.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True, "Connection successful"
    except MySQLError as exc:
        return False, str(exc)


# ─── Utility: Scalar Fetch ─────────────────────────────────────────────────────

def fetch_scalar(sql: str, params: tuple | list | None = None) -> Any:
    """
    Execute a query and return the first column of the first row (scalar).

    Useful for COUNT(*), SUM(), MAX(), etc.

    Returns None if no rows found.
    """
    row = execute_one(sql, params)
    if row is None:
        return None
    return next(iter(row.values()))


# ─── Standalone Test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    ok, message = test_connection()
    if ok:
        print(f"✅ Database connection: {message}")
        count = fetch_scalar("SELECT COUNT(*) FROM products")
        print(f"   Products in catalog: {count}")
    else:
        print(f"❌ Database connection failed: {message}")
