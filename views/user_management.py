"""
PaintPro Inventory Management System
=====================================
User Management Page  |  pages/user_management.py

Admin-only page to manage all system users:
View, create, edit, reset passwords, activate/deactivate.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.validators import validate_email, validate_phone, validate_name, validate_password
from models.user import UserModel
from config.constants import USER_ROLES_LIST
from utils.formatting import format_datetime, timeago


# ─── Dialogs ─────────────────────────────────────────────────────────────────

@st.dialog("Create / Edit User", width="large")
def _user_form_dialog(user_id: int = None):
    is_edit = user_id is not None
    user = {}
    if is_edit:
        user = UserModel.get_by_id(user_id) or {}

    st.markdown(f"### {'Edit User' if is_edit else 'Create New User'}")

    roles = UserModel.get_roles()
    role_names = [r["name"] for r in roles]
    role_labels = [r["display_name"] for r in roles]

    current_role = user.get("role_name", "employee")
    role_idx = role_names.index(current_role) if current_role in role_names else 0

    with st.form("user_form"):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full Name *", value=user.get("full_name", ""))
            email = st.text_input(
                "Email Address *",
                value=user.get("email", ""),
                disabled=is_edit,
            )
        with c2:
            phone = st.text_input("Phone", value=user.get("phone", ""))
            selected_role = st.selectbox(
                "Role *", options=role_names,
                format_func=lambda x: role_labels[role_names.index(x)],
                index=role_idx,
            )

        if not is_edit:
            st.markdown("---")
            cp1, cp2 = st.columns(2)
            with cp1:
                password = st.text_input("Password *", type="password")
            with cp2:
                password2 = st.text_input("Confirm Password *", type="password")

        is_active = st.checkbox("Account Active", value=bool(user.get("is_active", 1)))
        is_verified = st.checkbox("Email Verified", value=bool(user.get("is_verified", 1)))

        submitted = st.form_submit_button("Save User", type="primary", use_container_width=True)
        if submitted:
            errors = []
            ok, msg = validate_name(full_name, "Full Name"); not ok and errors.append(msg)
            if not is_edit:
                ok, msg = validate_email(email); not ok and errors.append(msg)
                ok, msg = validate_password(password); not ok and errors.append(msg)
                if password != password2:
                    errors.append("Passwords do not match.")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                uid = get_current_user()["id"]
                data = {
                    "full_name": full_name,
                    "phone": phone,
                    "role_name": selected_role,
                    "is_active": is_active,
                    "is_verified": is_verified,
                }
                if is_edit:
                    ok, err = UserModel.update(user_id, data, uid)
                else:
                    data["email"] = email
                    data["password"] = password
                    ok, err = UserModel.create(data, uid)

                if ok:
                    st.success("✅ User saved successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ {err}")


@st.dialog("Reset Password", width="small")
def _reset_password_dialog(user_id: int, user_name: str):
    st.markdown(f"### Reset Password for {user_name}")
    with st.form("reset_pw_form"):
        new_pw = st.text_input("New Password *", type="password")
        confirm_pw = st.text_input("Confirm Password *", type="password")
        submitted = st.form_submit_button("Reset Password", type="primary", use_container_width=True)
        if submitted:
            ok, msg = validate_password(new_pw)
            if not ok:
                st.error(f"❌ {msg}")
            elif new_pw != confirm_pw:
                st.error("❌ Passwords do not match.")
            else:
                uid = get_current_user()["id"]
                ok, err = UserModel.reset_password(user_id, new_pw, uid)
                if ok:
                    st.success("✅ Password reset successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ {err}")


# ─── Main Render ─────────────────────────────────────────────────────────────

def render():
    require_auth()

    me = get_current_user()
    if me["role"] != "admin":
        st.error("🚫 Access Denied - Admin only.")
        return

    st.markdown("## 🛡️ User Management")
    st.caption("Create, edit, deactivate, and manage all system users.")
    st.divider()

    # ─── Stats ───────────────────────────────────────────────────────────────
    stats = UserModel.get_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Users", stats.get("total", 0))
    c2.metric("Active", stats.get("active", 0))
    c3.metric("Inactive", stats.get("inactive", 0))
    c4.metric("Verified", stats.get("verified", 0))

    st.divider()

    # ─── Toolbar ─────────────────────────────────────────────────────────────
    t1, t2, t3 = st.columns([3, 1, 1])
    with t1:
        search = st.text_input("🔍 Search users", placeholder="Name, email, phone...",
                                label_visibility="collapsed")
    with t2:
        role_filter = st.selectbox("Role", ["All"] + USER_ROLES_LIST,
                                   label_visibility="collapsed")
    with t3:
        if st.button("➕ Create User", type="primary", use_container_width=True):
            _user_form_dialog()

    st.divider()

    # ─── Data ────────────────────────────────────────────────────────────────
    users = UserModel.get_all(search_query=search, role=role_filter)

    if not users:
        st.info("No users found matching your filters.")
        return

    role_colors = {
        "admin": "#FF4757",
        "manager": "#FFB703",
        "employee": "#00D4AA",
    }

    for u in users:
        rc = role_colors.get(u["role_name"], "#8B92A9")
        active_icon = "🟢" if u["is_active"] else "🔴"
        verified_icon = "✅" if u["is_verified"] else "⚠️"

        with st.container(border=True):
            col_info, col_meta, col_actions = st.columns([3, 2, 2])

            with col_info:
                initials = "".join(w[0].upper() for w in u["full_name"].split()[:2])
                st.markdown(
                    f"""
<div style="display:flex;align-items:center;gap:12px;">
  <div style="width:42px;height:42px;border-radius:50%;
              background:linear-gradient(135deg,{rc},#1a1a2e);
              display:flex;align-items:center;justify-content:center;
              font-weight:700;color:#fff;font-size:0.9rem;flex-shrink:0;">
    {initials}
  </div>
  <div>
    <div style="font-weight:700;font-size:1rem;">{u['full_name']}</div>
    <div style="font-size:0.8rem;color:#8B92A9;">{u['email']}</div>
    <div style="font-size:0.8rem;color:#8B92A9;">{u.get('phone') or '-'}</div>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with col_meta:
                st.markdown(
                    f"""
<div style="padding-top:4px;">
  <div style="margin-bottom:6px;">
    <span style="background:{rc}22;color:{rc};border:1px solid {rc}44;
                 padding:2px 10px;border-radius:20px;font-size:0.72rem;
                 font-weight:700;text-transform:uppercase;">
      {u['role_display']}
    </span>
  </div>
  <div style="font-size:0.8rem;color:#8B92A9;">
    {active_icon} {'Active' if u['is_active'] else 'Inactive'}
    &nbsp;&nbsp;{verified_icon} {'Verified' if u['is_verified'] else 'Unverified'}
  </div>
  <div style="font-size:0.75rem;color:#6B7280;margin-top:4px;">
    Last login: {timeago(u['last_login']) if u['last_login'] else 'Never'}
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with col_actions:
                a1, a2, a3 = st.columns(3)
                with a1:
                    if st.button("✏️", key=f"edit_u_{u['id']}", help="Edit user",
                                  use_container_width=True):
                        _user_form_dialog(u["id"])
                with a2:
                    if st.button("🔑", key=f"pw_u_{u['id']}", help="Reset password",
                                  use_container_width=True):
                        _reset_password_dialog(u["id"], u["full_name"])
                with a3:
                    toggle_label = "🔴" if u["is_active"] else "🟢"
                    toggle_help = "Deactivate" if u["is_active"] else "Activate"
                    if me["id"] != u["id"]:
                        if st.button(toggle_label, key=f"tog_u_{u['id']}", help=toggle_help,
                                      use_container_width=True):
                            UserModel.toggle_active(u["id"], not u["is_active"], me["id"])
                            st.rerun()
                    else:
                        st.markdown("&nbsp;", unsafe_allow_html=True)
