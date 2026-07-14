"""
PaintPro Inventory Management System
=====================================
User Model (DAO)  |  models/user.py

Data access object for the users table.
Provides create, read, update, deactivate operations.
"""

from database.connection import execute_query, execute_one, execute_write
from utils.auth import hash_password, log_activity


class UserModel:

    @staticmethod
    def get_all(search_query: str = "", role: str = "All") -> list[dict]:
        """Fetch all users with their role information."""
        sql = """
            SELECT u.id, u.full_name, u.email, u.phone, u.is_active, u.is_verified,
                   u.last_login, u.login_attempts, u.created_at,
                   r.name AS role_name, r.display_name AS role_display
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE 1=1
        """
        params = []

        if search_query:
            sql += " AND (u.full_name LIKE %s OR u.email LIKE %s OR u.phone LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val, val])

        if role and role != "All":
            sql += " AND r.name = %s"
            params.append(role.lower())

        sql += " ORDER BY u.created_at DESC"
        return execute_query(sql, tuple(params)) or []

    @staticmethod
    def get_by_id(user_id: int) -> dict:
        """Fetch a single user by ID."""
        return execute_one(
            """
            SELECT u.*, r.name AS role_name, r.display_name AS role_display
            FROM users u JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
            """,
            (user_id,),
        )

    @staticmethod
    def create(data: dict, created_by: int) -> tuple[bool, str]:
        """Create a new user account."""
        try:
            existing = execute_one(
                "SELECT id FROM users WHERE email = %s", (data["email"].lower(),)
            )
            if existing:
                return False, "An account with this email already exists."

            role = execute_one(
                "SELECT id FROM roles WHERE name = %s AND is_active = 1",
                (data["role_name"],),
            )
            if not role:
                return False, f"Role '{data['role_name']}' not found."

            pw_hash = hash_password(data["password"])
            new_id = execute_write(
                """
                INSERT INTO users (role_id, full_name, email, phone, password_hash,
                                   is_active, is_verified, created_by)
                VALUES (%s, %s, %s, %s, %s, 1, 1, %s)
                """,
                (
                    role["id"],
                    data["full_name"],
                    data["email"].lower(),
                    data.get("phone", ""),
                    pw_hash,
                    created_by,
                ),
                return_last_id=True,
            )
            log_activity(
                "create_user", "admin",
                f"Created user {data['email']}",
                user_id=created_by, entity_type="user", entity_id=new_id,
            )
            return True, ""
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def update(user_id: int, data: dict, updated_by: int) -> tuple[bool, str]:
        """Update a user's profile and role."""
        try:
            role = execute_one(
                "SELECT id FROM roles WHERE name = %s AND is_active = 1",
                (data["role_name"],),
            )
            if not role:
                return False, f"Role '{data['role_name']}' not found."

            execute_write(
                """
                UPDATE users SET role_id=%s, full_name=%s, phone=%s,
                                 is_active=%s, is_verified=%s
                WHERE id=%s
                """,
                (
                    role["id"],
                    data["full_name"],
                    data.get("phone", ""),
                    int(data.get("is_active", 1)),
                    int(data.get("is_verified", 1)),
                    user_id,
                ),
            )
            log_activity(
                "update_user", "admin",
                f"Updated user ID {user_id}",
                user_id=updated_by, entity_type="user", entity_id=user_id,
            )
            return True, ""
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def reset_password(user_id: int, new_password: str, updated_by: int) -> tuple[bool, str]:
        """Admin reset of a user's password."""
        try:
            pw_hash = hash_password(new_password)
            execute_write(
                "UPDATE users SET password_hash=%s, login_attempts=0, locked_until=NULL WHERE id=%s",
                (pw_hash, user_id),
            )
            log_activity(
                "admin_password_reset", "admin",
                f"Admin reset password for user ID {user_id}",
                user_id=updated_by, entity_type="user", entity_id=user_id,
            )
            return True, ""
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def toggle_active(user_id: int, is_active: bool, updated_by: int) -> tuple[bool, str]:
        """Activate or deactivate a user account."""
        try:
            execute_write(
                "UPDATE users SET is_active=%s WHERE id=%s",
                (int(is_active), user_id),
            )
            action = "activated" if is_active else "deactivated"
            log_activity(
                f"user_{action}", "admin",
                f"User ID {user_id} {action}",
                user_id=updated_by, entity_type="user", entity_id=user_id,
            )
            return True, ""
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def get_roles() -> list[dict]:
        """Fetch all active roles."""
        return execute_query(
            "SELECT id, name, display_name FROM roles WHERE is_active=1 ORDER BY id",
        ) or []

    @staticmethod
    def get_stats() -> dict:
        """Return aggregate user statistics."""
        row = execute_one(
            """
            SELECT
                COUNT(*) AS total,
                SUM(is_active=1) AS active,
                SUM(is_active=0) AS inactive,
                SUM(is_verified=1) AS verified
            FROM users
            """
        )
        return row or {"total": 0, "active": 0, "inactive": 0, "verified": 0}
