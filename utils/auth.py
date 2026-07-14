"""
PaintPro Inventory Management System
=====================================
Authentication Utilities  |  utils/auth.py

Provides:
  - Password hashing / verification (bcrypt)
  - User login / logout
  - Session management (Streamlit st.session_state)
  - Role-based access control (RBAC)
  - Password reset token generation
  - Activity logging for auth events
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import streamlit as st

from database.connection import execute_one, execute_write, execute_query
from config.constants import ROLE_PERMISSIONS, DB_DATETIME_FORMAT


# ─── Password Utilities ───────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plain-text password with bcrypt (cost=12)."""
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ─── Login / Logout ───────────────────────────────────────────────────────────

def login_user(email: str, password: str) -> tuple[bool, str]:
    """
    Authenticate a user by email + password.

    Returns:
        (True, "")           on success  - session is populated.
        (False, error_msg)   on failure.
    """
    email = email.strip().lower()

    if not email or not password:
        return False, "Email and password are required."

    # Fetch user record with role info
    user = execute_one(
        """
        SELECT u.id, u.full_name, u.email, u.phone, u.password_hash,
               u.is_active, u.is_verified, u.login_attempts, u.locked_until,
               u.avatar_path, u.created_at,
               r.name AS role_name, r.display_name AS role_display,
               r.permissions AS role_permissions
        FROM   users u
        JOIN   roles r ON u.role_id = r.id
        WHERE  u.email = %s
        """,
        (email,),
    )

    if not user:
        return False, "Invalid email or password."

    # Check account active
    if not user["is_active"]:
        return False, "Your account has been deactivated. Contact administrator."

    # Check account lock
    if user["locked_until"] and datetime.now() < user["locked_until"]:
        remaining = (user["locked_until"] - datetime.now()).seconds // 60
        return False, f"Account locked. Try again in {remaining + 1} minute(s)."

    # Verify password
    if not verify_password(password, user["password_hash"]):
        attempts = user["login_attempts"] + 1
        if attempts >= 5:
            locked_until = datetime.now() + timedelta(minutes=30)
            execute_write(
                "UPDATE users SET login_attempts=%s, locked_until=%s WHERE id=%s",
                (attempts, locked_until.strftime(DB_DATETIME_FORMAT), user["id"]),
            )
            return False, "Too many failed attempts. Account locked for 30 minutes."
        else:
            execute_write(
                "UPDATE users SET login_attempts=%s WHERE id=%s",
                (attempts, user["id"]),
            )
            return False, f"Invalid email or password. ({5 - attempts} attempt(s) remaining)"

    # Reset failed attempts and update last login
    execute_write(
        "UPDATE users SET login_attempts=0, locked_until=NULL, last_login=%s WHERE id=%s",
        (datetime.now().strftime(DB_DATETIME_FORMAT), user["id"]),
    )

    # Populate session
    _set_session(user)

    # Log activity
    log_activity(
        user_id=user["id"],
        action="user_login",
        module="auth",
        description=f"User '{user['full_name']}' logged in.",
    )

    return True, ""


def logout_user():
    """Clear all session state and redirect to login."""
    user_id   = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "Unknown")

    if user_id:
        log_activity(
            user_id=user_id,
            action="user_logout",
            module="auth",
            description=f"User '{user_name}' logged out.",
        )

    # Clear all session keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


def _set_session(user: dict):
    """Populate st.session_state from an authenticated user record."""
    import json

    permissions = user.get("role_permissions")
    if isinstance(permissions, str):
        try:
            permissions = json.loads(permissions)
        except Exception:
            permissions = []
    elif permissions is None:
        permissions = ROLE_PERMISSIONS.get(user["role_name"], [])

    st.session_state["authenticated"]   = True
    st.session_state["user_id"]         = user["id"]
    st.session_state["user_name"]       = user["full_name"]
    st.session_state["user_email"]      = user["email"]
    st.session_state["user_phone"]      = user.get("phone", "")
    st.session_state["user_role"]       = user["role_name"]
    st.session_state["role_display"]    = user.get("role_display", user["role_name"].title())
    st.session_state["permissions"]     = permissions
    st.session_state["avatar_path"]     = user.get("avatar_path", "")
    st.session_state["login_time"]      = datetime.now().isoformat()


# ─── Session Helpers ──────────────────────────────────────────────────────────

def is_authenticated() -> bool:
    """Return True if the current session has a valid authenticated user."""
    return bool(st.session_state.get("authenticated", False))


def get_current_user() -> dict:
    """Return the current session user dict (safe defaults if not logged in)."""
    return {
        "id":           st.session_state.get("user_id"),
        "name":         st.session_state.get("user_name", ""),
        "email":        st.session_state.get("user_email", ""),
        "phone":        st.session_state.get("user_phone", ""),
        "role":         st.session_state.get("user_role", ""),
        "role_display": st.session_state.get("role_display", ""),
        "permissions":  st.session_state.get("permissions", []),
        "avatar_path":  st.session_state.get("avatar_path", ""),
    }


def has_permission(page_key: str) -> bool:
    """Return True if the current user has access to the given page/module."""
    permissions = st.session_state.get("permissions", [])
    return page_key in permissions


def require_auth():
    """
    Guard function - call at the top of every page.
    Redirects to login if not authenticated.
    """
    if not is_authenticated():
        st.session_state["redirect_after_login"] = st.session_state.get("current_page", "")
        st.rerun()


def require_permission(page_key: str):
    """
    Guard function - call at the top of restricted pages.
    Shows access denied message if user lacks permission.
    """
    require_auth()
    if not has_permission(page_key):
        st.error("🚫 Access Denied - You don't have permission to view this page.")
        st.stop()


# ─── Registration ─────────────────────────────────────────────────────────────

def register_user(
    full_name: str,
    email: str,
    phone: str,
    password: str,
    role_name: str = "employee",
    created_by: Optional[int] = None,
) -> tuple[bool, str]:
    """
    Register a new user account.

    Returns:
        (True, "")             on success.
        (False, error_msg)     on validation / DB failure.
    """
    email = email.strip().lower()
    full_name = full_name.strip()

    # Check duplicate email
    existing = execute_one("SELECT id FROM users WHERE email = %s", (email,))
    if existing:
        return False, "An account with this email already exists."

    # Get role id
    role = execute_one("SELECT id FROM roles WHERE name = %s AND is_active = 1", (role_name,))
    if not role:
        return False, f"Role '{role_name}' not found."

    pw_hash = hash_password(password)

    user_id = execute_write(
        """
        INSERT INTO users (role_id, full_name, email, phone, password_hash,
                           is_active, is_verified, created_by)
        VALUES (%s, %s, %s, %s, %s, 1, 0, %s)
        """,
        (role["id"], full_name, email, phone, pw_hash, created_by),
        return_last_id=True,
    )

    if user_id:
        log_activity(
            user_id=created_by or user_id,
            action="user_registered",
            module="auth",
            description=f"New user '{full_name}' ({email}) registered with role '{role_name}'.",
            entity_type="user",
            entity_id=user_id,
        )
        return True, ""

    return False, "Registration failed. Please try again."


# ─── Password Reset ───────────────────────────────────────────────────────────

def generate_reset_token(email: str) -> tuple[bool, str]:
    """
    Generate a password reset token for the given email.

    Returns:
        (True, token)         - token to be sent via email.
        (False, error_msg)
    """
    email = email.strip().lower()
    user = execute_one("SELECT id, full_name FROM users WHERE email = %s AND is_active = 1", (email,))

    if not user:
        # Return success even for unknown emails (security: don't reveal user existence)
        return True, ""

    token   = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(hours=1)).strftime(DB_DATETIME_FORMAT)

    execute_write(
        "UPDATE users SET reset_token=%s, reset_token_expires=%s WHERE id=%s",
        (token, expires, user["id"]),
    )

    log_activity(
        user_id=user["id"],
        action="password_reset_requested",
        module="auth",
        description=f"Password reset token generated for '{user['full_name']}'.",
    )

    return True, token


def reset_password_with_token(token: str, new_password: str) -> tuple[bool, str]:
    """
    Reset a user's password using a valid reset token.

    Returns:
        (True, "")          on success.
        (False, error_msg)  on invalid/expired token.
    """
    user = execute_one(
        """
        SELECT id, full_name, reset_token_expires
        FROM   users
        WHERE  reset_token = %s AND is_active = 1
        """,
        (token,),
    )

    if not user:
        return False, "Invalid or expired reset link."

    if user["reset_token_expires"] and datetime.now() > user["reset_token_expires"]:
        return False, "This reset link has expired. Please request a new one."

    pw_hash = hash_password(new_password)
    execute_write(
        """
        UPDATE users
        SET    password_hash = %s,
               reset_token = NULL,
               reset_token_expires = NULL,
               login_attempts = 0,
               locked_until = NULL
        WHERE  id = %s
        """,
        (pw_hash, user["id"]),
    )

    log_activity(
        user_id=user["id"],
        action="password_reset_completed",
        module="auth",
        description=f"Password successfully reset for '{user['full_name']}'.",
    )

    return True, ""


def change_password(user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
    """Allow a logged-in user to change their own password."""
    user = execute_one("SELECT password_hash FROM users WHERE id=%s", (user_id,))
    if not user:
        return False, "User not found."

    if not verify_password(current_password, user["password_hash"]):
        return False, "Current password is incorrect."

    pw_hash = hash_password(new_password)
    execute_write("UPDATE users SET password_hash=%s WHERE id=%s", (pw_hash, user_id))

    log_activity(
        user_id=user_id,
        action="password_changed",
        module="auth",
        description="User changed their password.",
    )
    return True, ""


# ─── Profile Update ───────────────────────────────────────────────────────────

def update_profile(
    user_id: int,
    full_name: str,
    phone: str,
    avatar_path: Optional[str] = None,
) -> tuple[bool, str]:
    """Update the logged-in user's basic profile info."""
    try:
        if avatar_path:
            execute_write(
                "UPDATE users SET full_name=%s, phone=%s, avatar_path=%s WHERE id=%s",
                (full_name, phone, avatar_path, user_id),
            )
        else:
            execute_write(
                "UPDATE users SET full_name=%s, phone=%s WHERE id=%s",
                (full_name, phone, user_id),
            )

        # Refresh session
        st.session_state["user_name"]   = full_name
        st.session_state["user_phone"]  = phone
        if avatar_path:
            st.session_state["avatar_path"] = avatar_path

        log_activity(
            user_id=user_id,
            action="profile_updated",
            module="auth",
            description=f"Profile updated for user ID {user_id}.",
        )
        return True, ""
    except Exception as exc:
        return False, str(exc)


# ─── Activity Logging ─────────────────────────────────────────────────────────

def log_activity(
    action: str,
    module: str,
    description: str = "",
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
):
    """
    Insert a row into activity_logs.
    Silent on failure so it never disrupts user-facing operations.
    """
    import json

    uid = user_id or st.session_state.get("user_id")
    try:
        execute_write(
            """
            INSERT INTO activity_logs
                (user_id, action, module, description, entity_type, entity_id,
                 old_values, new_values)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uid,
                action,
                module,
                description,
                entity_type,
                entity_id,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
            ),
        )
    except Exception:
        pass  # Never let logging break the main flow
