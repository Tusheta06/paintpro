"""
PaintPro Inventory Management System
=====================================
Profile Page  |  pages/profile.py

Features:
  - View & edit user profile (name, phone, avatar)
  - Change password with current-password verification
  - View recent activity logs for the current user
  - Role & account metadata display
"""

import streamlit as st
from datetime import datetime

from utils.auth import (
    get_current_user,
    update_profile,
    change_password,
    require_auth,
    log_activity,
)
from utils.validators import (
    validate_name,
    validate_phone,
    validate_password,
    validate_required,
)
from utils.formatting import format_datetime, timeago, format_date
from database.connection import execute_query


def _load_activity_log(user_id: int, limit: int = 20) -> list[dict]:
    """Fetch recent activity entries for the current user."""
    return execute_query(
        """
        SELECT action, module, description, created_at
        FROM   activity_logs
        WHERE  user_id = %s
        ORDER  BY created_at DESC
        LIMIT  %s
        """,
        (user_id, limit),
    )


def _get_user_stats(user_id: int) -> dict:
    """Fetch sales count and total for this user."""
    from database.connection import execute_one, fetch_scalar

    sales_count = fetch_scalar(
        "SELECT COUNT(*) FROM sales WHERE created_by = %s AND status != 'cancelled'",
        (user_id,),
    ) or 0

    sales_total = fetch_scalar(
        "SELECT COALESCE(SUM(grand_total), 0) FROM sales WHERE created_by = %s AND status != 'cancelled'",
        (user_id,),
    ) or 0

    purchases_count = fetch_scalar(
        "SELECT COUNT(*) FROM purchases WHERE created_by = %s AND status != 'cancelled'",
        (user_id,),
    ) or 0

    activity_count = fetch_scalar(
        "SELECT COUNT(*) FROM activity_logs WHERE user_id = %s",
        (user_id,),
    ) or 0

    return {
        "sales_count":      int(sales_count),
        "sales_total":      float(sales_total),
        "purchases_count":  int(purchases_count),
        "activity_count":   int(activity_count),
    }


# ─── Main Render ─────────────────────────────────────────────────────────────

def render():
    """Render the full profile page."""
    require_auth()

    user = get_current_user()

    # ── Page Header ──────────────────────────────────────────────────────────
    initials = "".join(w[0].upper() for w in user["name"].split()[:2]) or "U"
    role_colors = {
        "admin":    ("#6C63FF", "Administrator"),
        "manager":  ("#00D4AA", "Manager"),
        "employee": ("#FFB703", "Employee"),
    }
    role_color, role_label = role_colors.get(user["role"], ("#8B92A9", "User"))

    st.markdown(
        f"""
<div style="background:linear-gradient(135deg,#1E2130,#252840);
            border:1px solid #2D3250;border-radius:16px;
            padding:32px;margin-bottom:28px;
            display:flex;align-items:center;gap:24px;">
  <div style="width:90px;height:90px;border-radius:50%;
              background:linear-gradient(135deg,{role_color},{role_color}88);
              display:flex;align-items:center;justify-content:center;
              font-size:2rem;font-weight:800;color:#fff;
              border:3px solid {role_color}55;flex-shrink:0;
              box-shadow:0 0 24px {role_color}44;">
    {initials}
  </div>
  <div style="flex:1;">
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-0.5px;">
      {user['name']}
    </div>
    <div style="color:#8B92A9;font-size:0.875rem;margin-top:4px;">{user['email']}</div>
    <div style="margin-top:10px;">
      <span style="background:{role_color}22;color:{role_color};border:1px solid {role_color}44;
                   padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:700;">
        ● {role_label}
      </span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Stats Row ─────────────────────────────────────────────────────────────
    stats = _get_user_stats(user["id"])

    s1, s2, s3, s4 = st.columns(4)
    for col, label, val, icon in [
        (s1, "Sales Created",   stats["sales_count"],     "🛒"),
        (s2, "Revenue Generated", f"₹{stats['sales_total']:,.0f}", "💰"),
        (s3, "Purchases Created", stats["purchases_count"], "📦"),
        (s4, "Total Actions",   stats["activity_count"],  "📋"),
    ]:
        with col:
            st.markdown(
                f"""
<div style="background:#1E2130;border:1px solid #2D3250;
            border-radius:12px;padding:18px 20px;text-align:center;">
  <div style="font-size:1.6rem;margin-bottom:6px;">{icon}</div>
  <div style="font-size:1.4rem;font-weight:800;color:#fff;">{val}</div>
  <div style="font-size:0.75rem;color:#8B92A9;margin-top:4px;">{label}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_profile, tab_password, tab_activity = st.tabs(
        ["✏️ Edit Profile", "🔒 Change Password", "📋 Activity Log"]
    )

    # ── Tab 1: Edit Profile ───────────────────────────────────────────────────
    with tab_profile:
        st.markdown("### Edit Profile Information")
        st.markdown(
            "<div style='color:#8B92A9;font-size:0.85rem;margin-bottom:20px;'>"
            "Update your display name and contact phone number.</div>",
            unsafe_allow_html=True,
        )

        col_form, col_info = st.columns([2, 1], gap="large")

        with col_form:
            with st.form("profile_form"):
                full_name = st.text_input(
                    "Full Name",
                    value=user["name"],
                    placeholder="Your full name",
                )
                email_display = st.text_input(
                    "Email Address (read-only)",
                    value=user["email"],
                    disabled=True,
                )
                phone = st.text_input(
                    "Phone Number",
                    value=user.get("phone", ""),
                    placeholder="10-digit mobile number",
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "💾 Save Changes", use_container_width=True, type="primary"
                )

                if submitted:
                    errors = []
                    ok, msg = validate_name(full_name, "Full Name")
                    not ok and errors.append(msg)
                    ok, msg = validate_phone(phone)
                    not ok and errors.append(msg)

                    if errors:
                        for err in errors:
                            st.error(f"❌ {err}")
                    else:
                        success, message = update_profile(user["id"], full_name, phone)
                        if success:
                            st.success("✅ Profile updated successfully!")
                        else:
                            st.error(f"❌ {message}")

        with col_info:
            st.markdown(
                f"""
<div style="background:#1A1D27;border:1px solid #2D3250;
            border-radius:12px;padding:20px;">
  <div style="font-size:0.8rem;font-weight:700;color:#8B92A9;
              text-transform:uppercase;letter-spacing:0.8px;margin-bottom:14px;">
    Account Details
  </div>
  <div style="display:flex;flex-direction:column;gap:12px;">
    <div>
      <div style="font-size:0.72rem;color:#8B92A9;">User ID</div>
      <div style="font-size:0.875rem;color:#fff;font-family:monospace;">
        #PP-{user['id']:04d}
      </div>
    </div>
    <div>
      <div style="font-size:0.72rem;color:#8B92A9;">Role</div>
      <div style="font-size:0.875rem;color:{role_color};font-weight:600;">
        {role_label}
      </div>
    </div>
    <div>
      <div style="font-size:0.72rem;color:#8B92A9;">Account Status</div>
      <div style="font-size:0.875rem;color:#00D4AA;font-weight:600;">
        ✓ Active
      </div>
    </div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    # ── Tab 2: Change Password ────────────────────────────────────────────────
    with tab_password:
        st.markdown("### Change Password")
        st.markdown(
            "<div style='color:#8B92A9;font-size:0.85rem;margin-bottom:20px;'>"
            "Choose a strong password: 8+ chars with uppercase, lowercase, digit & symbol."
            "</div>",
            unsafe_allow_html=True,
        )

        _, pwd_col, _ = st.columns([0.5, 2, 0.5])
        with pwd_col:
            with st.form("password_form"):
                current_pw = st.text_input("🔒 Current Password", type="password")
                new_pw     = st.text_input("🔑 New Password",     type="password")
                confirm_pw = st.text_input("🔑 Confirm New Password", type="password")

                # Policy hints
                st.markdown(
                    """
<div style="background:#1A1D27;border:1px solid #2D3250;border-radius:8px;
            padding:12px 14px;margin-top:4px;">
  <div style="font-size:0.75rem;color:#8B92A9;font-weight:700;margin-bottom:6px;">
    PASSWORD POLICY
  </div>
  <div style="font-size:0.75rem;color:#B8BDD9;display:flex;flex-direction:column;gap:3px;">
    <span>✓ Minimum 8 characters</span>
    <span>✓ At least one uppercase letter (A–Z)</span>
    <span>✓ At least one lowercase letter (a–z)</span>
    <span>✓ At least one digit (0–9)</span>
    <span>✓ At least one special character (!@#$...)</span>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "🔐 Update Password", use_container_width=True, type="primary"
                )

                if submitted:
                    errors = []
                    ok, msg = validate_required(current_pw, "Current password")
                    not ok and errors.append(msg)
                    ok, msg = validate_password(new_pw)
                    not ok and errors.append(msg)
                    if new_pw != confirm_pw:
                        errors.append("New passwords do not match.")
                    if new_pw == current_pw:
                        errors.append("New password must be different from current password.")

                    if errors:
                        for err in errors:
                            st.error(f"❌ {err}")
                    else:
                        success, message = change_password(user["id"], current_pw, new_pw)
                        if success:
                            st.success("✅ Password changed successfully!")
                        else:
                            st.error(f"❌ {message}")

    # ── Tab 3: Activity Log ───────────────────────────────────────────────────
    with tab_activity:
        st.markdown("### My Recent Activity")
        st.markdown(
            "<div style='color:#8B92A9;font-size:0.85rem;margin-bottom:20px;'>"
            "Last 20 actions performed by your account.</div>",
            unsafe_allow_html=True,
        )

        logs = _load_activity_log(user["id"])

        if not logs:
            st.markdown(
                """
<div style="text-align:center;padding:48px;color:#8B92A9;">
  <div style="font-size:3rem;margin-bottom:12px;">📋</div>
  <div style="font-size:1rem;font-weight:700;color:#B8BDD9;">No activity yet</div>
  <div style="font-size:0.85rem;">Your actions will appear here.</div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            module_icons = {
                "auth":      "🔐",
                "inventory": "📦",
                "sales":     "💰",
                "purchases": "🛒",
                "customers": "👥",
                "suppliers": "🏭",
                "stock":     "📊",
                "reports":   "📄",
                "settings":  "⚙️",
            }

            rows_html = ""
            for log in logs:
                icon = module_icons.get(log.get("module", ""), "📌")
                when = timeago(log.get("created_at"))
                desc = log.get("description", "-")
                mod  = (log.get("module") or "system").title()
                act  = (log.get("action") or "action").replace("_", " ").title()

                rows_html += f"""
<tr>
  <td style="padding:13px 16px;">
    <span style="font-size:1.2rem;">{icon}</span>
  </td>
  <td style="padding:13px 16px;">
    <div style="font-weight:600;color:#fff;font-size:0.875rem;">{act}</div>
    <div style="color:#8B92A9;font-size:0.78rem;margin-top:2px;">{desc}</div>
  </td>
  <td style="padding:13px 16px;">
    <span style="background:rgba(108,99,255,0.15);color:#8B85FF;
                 border:1px solid rgba(108,99,255,0.25);
                 padding:2px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;">
      {mod}
    </span>
  </td>
  <td style="padding:13px 16px;color:#8B92A9;font-size:0.8rem;white-space:nowrap;">
    {when}
  </td>
</tr>
"""

            st.markdown(
                f"""
<div style="background:#1E2130;border:1px solid #2D3250;border-radius:12px;overflow:hidden;">
  <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
    <thead>
      <tr style="background:#1A1D27;border-bottom:1px solid #2D3250;">
        <th style="padding:12px 16px;text-align:left;font-size:0.72rem;
                   font-weight:700;color:#8B92A9;text-transform:uppercase;
                   letter-spacing:0.8px;width:40px;"></th>
        <th style="padding:12px 16px;text-align:left;font-size:0.72rem;
                   font-weight:700;color:#8B92A9;text-transform:uppercase;
                   letter-spacing:0.8px;">Action</th>
        <th style="padding:12px 16px;text-align:left;font-size:0.72rem;
                   font-weight:700;color:#8B92A9;text-transform:uppercase;
                   letter-spacing:0.8px;">Module</th>
        <th style="padding:12px 16px;text-align:left;font-size:0.72rem;
                   font-weight:700;color:#8B92A9;text-transform:uppercase;
                   letter-spacing:0.8px;">When</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""",
                unsafe_allow_html=True,
            )
