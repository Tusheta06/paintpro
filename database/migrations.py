"""
PaintPro Inventory Management System
=====================================
Database Migration Runner  |  database/migrations.py

Responsibilities:
  1. Create the database if it doesn't exist
  2. Execute schema.sql (DDL)
  3. Execute seed_data.sql (initial data) - skipped if already seeded
  4. Hash the default user passwords properly using bcrypt
  5. Create required OS directories (uploads, reports)

Usage:
  python database/migrations.py              # full migration
  python database/migrations.py --schema-only
  python database/migrations.py --seed-only
  python database/migrations.py --reset      # ⚠ drops & recreates DB
"""

import sys
import os
import argparse
import bcrypt
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import mysql.connector
from mysql.connector import Error as MySQLError
from config.settings import db_config
from config.constants import DB_DATETIME_FORMAT

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent
SCHEMA_FILE  = Path(__file__).parent / "schema.sql"
SEED_FILE    = Path(__file__).parent / "seed_data.sql"

# ─── Default user credentials (will be bcrypt-hashed) ────────────────────────
DEFAULT_USERS = [
    {
        "role_name":   "admin",
        "full_name":   "System Administrator",
        "email":       "admin@paintpro.com",
        "phone":       "9876543210",
        "password":    "Admin@123",
        "is_verified": 1,
    },
    {
        "role_name":   "manager",
        "full_name":   "Store Manager",
        "email":       "manager@paintpro.com",
        "phone":       "9876543211",
        "password":    "Manager@123",
        "is_verified": 1,
    },
    {
        "role_name":   "employee",
        "full_name":   "Sales Employee",
        "email":       "employee@paintpro.com",
        "phone":       "9876543212",
        "password":    "Employee@123",
        "is_verified": 1,
    },
]


def get_root_connection():
    """Connect to MySQL server WITHOUT specifying a database (for initial setup)."""
    try:
        conn = mysql.connector.connect(
            host=db_config.HOST,
            port=db_config.PORT,
            user=db_config.USER,
            password=db_config.PASSWORD,
            charset=db_config.CHARSET,
            autocommit=True,
        )
        return conn
    except MySQLError as exc:
        print(f"  ❌ Cannot connect to MySQL: {exc}")
        print(f"     Host: {db_config.HOST}:{db_config.PORT}  User: {db_config.USER}")
        sys.exit(1)


def get_db_connection():
    """Connect to MySQL with the target paintpro_db database."""
    try:
        conn = mysql.connector.connect(
            host=db_config.HOST,
            port=db_config.PORT,
            database=db_config.NAME,
            user=db_config.USER,
            password=db_config.PASSWORD,
            charset=db_config.CHARSET,
            autocommit=False,
        )
        return conn
    except MySQLError as exc:
        print(f"  ❌ Cannot connect to {db_config.NAME}: {exc}")
        sys.exit(1)


def create_database(conn, reset: bool = False):
    """Create the database (with optional DROP for reset mode)."""
    cursor = conn.cursor()
    if reset:
        print(f"  ⚠️  Dropping database '{db_config.NAME}' (reset mode)…")
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_config.NAME}`")
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_config.NAME}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
    )
    cursor.close()
    print(f"  ✅ Database '{db_config.NAME}' ready.")


def execute_sql_file(conn, filepath: Path, label: str):
    """
    Execute a .sql file split by statement delimiters.
    Handles DELIMITER changes for triggers/procedures.
    """
    print(f"  📄 Executing {label}…")
    cursor = conn.cursor()
    sql_content = filepath.read_text(encoding="utf-8")

    # Split on DELIMITER changes for trigger blocks
    delimiter     = ";"
    statements    = []
    current_stmt  = []
    custom_delim  = None

    for line in sql_content.splitlines():
        stripped = line.strip()

        # Skip comments and blank lines
        if not stripped or stripped.startswith("--") or stripped.startswith("#"):
            continue

        # Handle DELIMITER directive
        if stripped.upper().startswith("DELIMITER"):
            parts = stripped.split()
            if len(parts) >= 2:
                custom_delim = parts[1].strip() if parts[1].strip() != ";" else None
                delimiter = parts[1].strip()
            continue

        current_stmt.append(line)

        # Check end of statement
        effective_delim = custom_delim if custom_delim else ";"
        if stripped.endswith(effective_delim):
            stmt = "\n".join(current_stmt).strip()
            if custom_delim:
                stmt = stmt[: -len(custom_delim)].strip()
            if stmt:
                statements.append(stmt)
            current_stmt = []

    executed = 0
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
            conn.commit()
            executed += 1
        except MySQLError as exc:
            # Ignore 'already exists' errors gracefully
            if exc.errno in (1050, 1060, 1061, 1062, 1304, 1359, 1394):
                pass  # Table/column/index/trigger already exists
            else:
                conn.rollback()
                raise Exception(f"Failed to execute schema block:\n\n{stmt[:200]}...\n\nError {exc.errno}: {exc.msg}")

    cursor.close()
    print(f"  ✅ {label} - {executed} statement(s) executed.")


def seed_default_users(conn):
    """
    Insert / update the default users with properly bcrypt-hashed passwords.
    This replaces the placeholder hashes from seed_data.sql.
    """
    print("  🔐 Hashing default user passwords…")
    cursor = conn.cursor(dictionary=True)

    # Get role id map
    cursor.execute("SELECT id, name FROM roles")
    role_map = {row["name"]: row["id"] for row in cursor.fetchall()}

    for user in DEFAULT_USERS:
        role_id = role_map.get(user["role_name"])
        if not role_id:
            print(f"     ⚠️  Role '{user['role_name']}' not found - skipping {user['email']}")
            continue

        pw_hash = bcrypt.hashpw(
            user["password"].encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        cursor.execute("SELECT id FROM users WHERE email = %s", (user["email"],))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE users SET password_hash = %s, is_verified = %s WHERE email = %s",
                (pw_hash, user["is_verified"], user["email"]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO users (role_id, full_name, email, phone, password_hash, is_active, is_verified)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
                """,
                (role_id, user["full_name"], user["email"], user["phone"],
                 pw_hash, user["is_verified"]),
            )
        print(f"     ✅ {user['email']} ({user['role_name']}) - password hashed")

    conn.commit()
    cursor.close()


def create_required_directories():
    """Create OS directories needed for file uploads and reports."""
    dirs = [
        BASE_DIR / "assets" / "images" / "products",
        BASE_DIR / "assets" / "images" / "avatars",
        BASE_DIR / "assets" / "images" / "logos",
        BASE_DIR / "reports",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  ✅ Upload and report directories verified.")


def is_database_seeded(conn) -> bool:
    """Return True if the database already has category records (seeded)."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0


def run_migration(schema_only: bool = False, seed_only: bool = False, reset: bool = False):
    """Main migration orchestration."""
    print("\n" + "=" * 60)
    print("  🎨 PaintPro IMS - Database Migration")
    print("=" * 60)

    # Step 1: Create DB
    if not seed_only:
        root_conn = get_root_connection()
        create_database(root_conn, reset=reset)
        root_conn.close()

    # Step 2: Schema
    if not seed_only:
        db_conn = get_db_connection()
        execute_sql_file(db_conn, SCHEMA_FILE, "schema.sql (DDL)")
        db_conn.close()

    # Step 3: Seed data
    if not schema_only:
        db_conn = get_db_connection()
        if not is_database_seeded(db_conn) or seed_only or reset:
            execute_sql_file(db_conn, SEED_FILE, "seed_data.sql")
        else:
            print("  ℹ️  Seed data already present - skipping.")
        db_conn.close()

    # Step 4: Hash passwords
    if not schema_only:
        db_conn = get_db_connection()
        seed_default_users(db_conn)
        db_conn.close()

    # Step 5: Directories
    create_required_directories()

    print("\n" + "=" * 60)
    print("  ✅ Migration Complete!")
    print("=" * 60)
    print(f"\n  Database : {db_config.NAME}  @  {db_config.HOST}:{db_config.PORT}")
    print("\n  Default Credentials:")
    for u in DEFAULT_USERS:
        print(f"    {u['email']:<35} → {u['password']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="PaintPro DB Migration Runner")
    parser.add_argument("--schema-only", action="store_true",
                        help="Run DDL schema only (skip seed data)")
    parser.add_argument("--seed-only",   action="store_true",
                        help="Run seed data only (skip schema)")
    parser.add_argument("--reset",       action="store_true",
                        help="⚠️  DROP and recreate the database from scratch")
    args = parser.parse_args()

    if args.reset:
        confirm = input(
            "  ⚠️  This will DROP all data in paintpro_db. "
            "Type 'YES' to confirm: "
        )
        if confirm.strip().upper() != "YES":
            print("  ❌ Reset cancelled.")
            sys.exit(0)

    run_migration(
        schema_only=args.schema_only,
        seed_only=args.seed_only,
        reset=args.reset,
    )


if __name__ == "__main__":
    main()
