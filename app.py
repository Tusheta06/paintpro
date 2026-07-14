"""
PaintPro Inventory Management System
=====================================
Main Application Entry Point  |  app.py

Handles:
  - Streamlit page config & CSS injection
  - Authentication routing (login / register / forgot-password / reset)
  - Native Streamlit sidebar navigation rendering
  - Page dispatch based on session state
"""

import streamlit as st
from pathlib import Path

# ─── Page Config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="PaintPro IMS",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help":     "https://github.com/paintpro-ims",
        "Report a bug": "https://github.com/paintpro-ims/issues",
        "About":        "PaintPro IMS v1.0.0 - Modern Paint Store Management",
    },
)

# ─── CSS Injection ────────────────────────────────────────────────────────────

def _load_css():
    """Inject the main CSS design system into the Streamlit app."""
    css_path = Path("assets/css/main.css")
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    # Fonts & Icons CDN
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Sora:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""",
        unsafe_allow_html=True,
    )

_load_css()



# ─── Logo Helper ─────────────────────────────────────────────────────────────
import base64 as _b64

def _get_logo_b64() -> str:
    """Return the PaintPro logo as a base64-encoded data URI."""
    logo_path = Path("assets/images/logo.png")
    if logo_path.exists():
        return _b64.b64encode(logo_path.read_bytes()).decode()
    return ""

_LOGO_B64 = _get_logo_b64()

# ─── Imports (after page config) ─────────────────────────────────────────────
from utils.auth import is_authenticated, logout_user, get_current_user, has_permission
from database.connection import test_connection

# ─── Session Defaults ─────────────────────────────────────────────────────────

def _init_session():
    """Initialize default session state variables."""
    defaults = {
        "authenticated":      False,
        "current_page":       "dashboard",
        "theme":              "dark",
        "auth_view":          "login",      # login | register | forgot | reset
        "notification_count": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_session()

# ─── DB Health Check ──────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def _db_ok() -> tuple[bool, str]:
    return test_connection()

# ─── Navigation Map ───────────────────────────────────────────────────────────

NAV_SECTIONS = [
    {
        "label": "Overview",
        "items": [
            {"key": "dashboard",     "label": "Dashboard",       "icon": "📊"},
            {"key": "analytics",     "label": "Analytics",       "icon": "📈"},
            {"key": "notifications", "label": "Notifications",   "icon": "🔔", "badge": "notification_count"},
        ],
    },
    {
        "label": "Inventory",
        "items": [
            {"key": "inventory",        "label": "Products",        "icon": "📦"},
            {"key": "categories",       "label": "Categories",      "icon": "🗂️"},
            {"key": "brands",           "label": "Brands",          "icon": "🏷️"},
            {"key": "stock_management", "label": "Stock Management","icon": "🏭"},
        ],
    },
    {
        "label": "Business",
        "items": [
            {"key": "purchases", "label": "Purchases", "icon": "🛒"},
            {"key": "sales",     "label": "Sales",     "icon": "💰"},
            {"key": "customers", "label": "Customers", "icon": "👥"},
            {"key": "suppliers", "label": "Suppliers", "icon": "🚚"},
        ],
    },
    {
        "label": "Reports & Export",
        "items": [
            {"key": "reports",       "label": "Reports",       "icon": "📋"},
            {"key": "export_center", "label": "Export Center", "icon": "⬇️"},
        ],
    },
    {
        "label": "Administration",
        "items": [
            {"key": "user_management", "label": "User Management", "icon": "🛡️"},
            {"key": "settings",        "label": "Settings",        "icon": "⚙️"},
            {"key": "profile",         "label": "My Profile",      "icon": "👤"},
        ],
    },
]

# ─── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    """Render the native Streamlit sidebar with navigation."""
    from utils.notifications import get_system_notifications
    st.session_state["notification_count"] = len(get_system_notifications())

    user    = get_current_user()
    current = st.session_state.get("current_page", "dashboard")
    initials = "".join(w[0].upper() for w in user["name"].split()[:2]) if user["name"] else "U"

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────
        if _LOGO_B64:
            st.markdown(
                f'<div style="padding:8px 0 4px;text-align:center;">'
                f'<img src="data:image/png;base64,{_LOGO_B64}" '
                f'style="width:80%;max-width:180px;height:auto;border-radius:8px;" />'
                f'<div style="font-size:0.68rem;color:#8B92A9;margin-top:4px;">'
                f'Inventory Management System</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
<div style="padding:12px 0 8px;text-align:center;">
  <div style="font-size:2.2rem;line-height:1;">🎨</div>
  <div style="font-size:1.3rem;font-weight:900;letter-spacing:-0.5px;margin-top:4px;">
    Paint<span style="color:#6C63FF;">Pro</span>
  </div>
  <div style="font-size:0.68rem;color:#8B92A9;margin-top:2px;">Inventory Management</div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Navigation ────────────────────────────────────────────
        for section in NAV_SECTIONS:
            st.markdown(
                f"<div style='font-size:0.68rem;font-weight:700;color:#8B92A9;"
                f"text-transform:uppercase;letter-spacing:1.2px;"
                f"padding:8px 0 4px;'>{section['label']}</div>",
                unsafe_allow_html=True,
            )
            for item in section["items"]:
                if not has_permission(item["key"]):
                    continue

                badge_str = ""
                if "badge" in item:
                    count = st.session_state.get(item["badge"], 0)
                    if count and count > 0:
                        badge_str = f"  🔴 {count}"

                is_active = item["key"] == current
                btn_label = f"{item['icon']}  {item['label']}{badge_str}"

                if st.button(
                    btn_label,
                    key=f"nav_{item['key']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state["current_page"] = item["key"]
                    st.rerun()

        st.divider()

        # ── User Card ─────────────────────────────────────────────
        role_color = {
            "admin":    "#6C63FF",
            "manager":  "#00D4AA",
            "employee": "#FFB703",
        }.get(user["role"], "#8B92A9")

        st.markdown(
            f"""
<div style="display:flex;align-items:center;gap:10px;padding:4px 0 8px;">
  <div style="width:36px;height:36px;border-radius:50%;flex-shrink:0;
              background:linear-gradient(135deg,#6C63FF,#FF6B6B);
              display:flex;align-items:center;justify-content:center;
              font-size:0.85rem;font-weight:700;color:#fff;">
    {initials}
  </div>
  <div style="overflow:hidden;">
    <div style="font-size:0.82rem;font-weight:600;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
      {user['name']}
    </div>
    <div style="font-size:0.7rem;color:{role_color};">
      ● {user['role_display']}
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("🚪  Logout", key="sidebar_logout", use_container_width=True):
            logout_user()


# ─── Auth Pages ───────────────────────────────────────────────────────────────

def render_login_page():
    """Render the professional login page."""
    from utils.auth import login_user
    from utils.validators import validate_email, validate_required

    col_brand, col_form = st.columns([1, 1], gap="medium")

    import textwrap
    with col_brand:
        logo_img_tag = (
            f'<img src="data:image/png;base64,{_LOGO_B64}" '
            f'style="width:75%;max-width:280px;height:auto;'
            f'background:#fff;border-radius:16px;'
            f'padding:16px 20px;margin-bottom:24px;'
            f'box-shadow:0 8px 32px rgba(0,0,0,0.25);" />'
            if _LOGO_B64 else
            '<div style="font-size:4rem;margin-bottom:16px;">🎨</div>'
            '<div style="font-size:2.5rem;font-weight:900;color:#fff;letter-spacing:-1.5px;margin-bottom:8px;">'
            'Paint<span style="color:#FFB703;">Pro</span> IMS</div>'
        )
        html_content = textwrap.dedent(f"""
<div class="auth-brand-panel" style="
    background: linear-gradient(135deg, #6C63FF 0%, #4B44CC 50%, #2D1B8E 100%);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 40px;
    border-radius: 0 20px 20px 0;
    position: relative;
    overflow: hidden;
">
  <div style="position:relative;z-index:1;text-align:center;max-width:380px;">
    {logo_img_tag}
    <div style="color:rgba(255,255,255,0.75);font-size:0.95rem;margin-bottom:48px;">
      Modern Inventory Management for Paint Professionals
    </div>

""")
        st.markdown(html_content, unsafe_allow_html=True)

    # Form panel

    with col_form:
        _, form_col, _ = st.columns([0.5, 3, 0.5])
        with form_col:
            st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
            st.markdown(
                """
<div style="margin-bottom:8px;">
  <span style="font-size:1.6rem;font-weight:800;letter-spacing:-0.5px;">Welcome back 👋</span><br>
  <span style="color:#8B92A9;font-size:0.875rem;">Sign in to your PaintPro account</span>
</div>
<div style="height:24px;"></div>
""",
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("📧 Email Address", placeholder="admin@paintpro.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

                submitted = st.form_submit_button(
                    "Sign In →",
                    use_container_width=True,
                    type="primary",
                )

                if submitted:
                    ok_e, err_e = validate_email(email)
                    ok_p, err_p = validate_required(password, "Password")

                    if not ok_e:
                        st.error(f"❌ {err_e}")
                    elif not ok_p:
                        st.error(f"❌ {err_p}")
                    else:
                        with st.spinner("Signing in…"):
                            success, message = login_user(email, password)
                        if success:
                            st.success("✅ Login successful! Redirecting…")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            col_reg, col_forgot = st.columns(2)
            with col_reg:
                if st.button("Create Account", key="go_register", use_container_width=True):
                    st.session_state["auth_view"] = "register"
                    st.rerun()
            with col_forgot:
                if st.button("Forgot Password?", key="go_forgot", use_container_width=True):
                    st.session_state["auth_view"] = "forgot"
                    st.rerun()

            st.markdown("<hr style='margin:24px 0;border-color:#2D3250;'>", unsafe_allow_html=True)

            st.markdown(
                """
<div style="background:rgba(108,99,255,0.1);border:1px solid rgba(108,99,255,0.25);
            border-radius:10px;padding:14px 16px;">
  <div style="font-size:0.8rem;font-weight:700;color:#8B85FF;margin-bottom:8px;">
    🔑 Demo Credentials
  </div>
  <div style="font-size:0.78rem;color:#B8BDD9;display:grid;grid-template-columns:1fr 1fr;gap:4px;">
    <span>Admin:</span><span style="font-family:monospace;">Admin@123</span>
    <span>Manager:</span><span style="font-family:monospace;">Manager@123</span>
    <span>Employee:</span><span style="font-family:monospace;">Employee@123</span>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_register_page():
    """Render the registration page."""
    from utils.auth import register_user
    from utils.validators import validate_email, validate_password, validate_phone, validate_name

    st.markdown(
        """
<div style="text-align:center;padding:40px 0 20px;">
  <div style="font-size:2rem;font-weight:800;letter-spacing:-0.5px;">Create Account</div>
  <div style="color:#8B92A9;margin-top:6px;">Join PaintPro IMS today</div>
</div>
""",
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        with st.form("register_form"):
            full_name = st.text_input("👤 Full Name",     placeholder="John Doe")
            email     = st.text_input("📧 Email Address", placeholder="john@example.com")
            phone     = st.text_input("📱 Phone Number",  placeholder="9876543210")

            col_pw1, col_pw2 = st.columns(2)
            with col_pw1:
                password  = st.text_input("🔒 Password",         type="password")
            with col_pw2:
                password2 = st.text_input("🔒 Confirm Password", type="password")

            st.caption("Password must have 8+ chars, uppercase, lowercase, digit & special character.")

            submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

            if submitted:
                errors = []
                ok, msg = validate_name(full_name, "Full Name");    not ok and errors.append(msg)
                ok, msg = validate_email(email);                     not ok and errors.append(msg)
                ok, msg = validate_phone(phone);                     not ok and errors.append(msg)
                ok, msg = validate_password(password);               not ok and errors.append(msg)
                if password != password2:
                    errors.append("Passwords do not match.")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    with st.spinner("Creating account…"):
                        success, message = register_user(full_name, email, phone, password, "employee")
                    if success:
                        st.success("✅ Account created! Please sign in.")
                        st.session_state["auth_view"] = "login"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        if st.button("← Back to Login", key="back_to_login"):
            st.session_state["auth_view"] = "login"
            st.rerun()


def render_forgot_password_page():
    """Render the forgot password page."""
    from utils.auth import generate_reset_token

    st.markdown(
        """
<div style="text-align:center;padding:40px 0 20px;">
  <div style="font-size:2rem;font-weight:800;">Forgot Password 🔑</div>
  <div style="color:#8B92A9;margin-top:6px;">
    Enter your email and we'll send a reset link.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        with st.form("forgot_form"):
            email     = st.text_input("📧 Email Address", placeholder="your@email.com")
            submitted = st.form_submit_button("Send Reset Link →", use_container_width=True, type="primary")

            if submitted and email:
                ok, token = generate_reset_token(email)
                st.success(
                    "✅ If this email is registered, a reset link has been sent.\n\n"
                    "**For demo purposes, your reset token is:**"
                )
                if token:
                    st.code(token)
                    st.info("Copy this token and use it on the Reset Password page.")
                    st.session_state["_reset_token_demo"] = token

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Login", key="forgot_back"):
                st.session_state["auth_view"] = "login"
                st.rerun()
        with col2:
            if st.button("Enter Reset Token →", key="go_reset"):
                st.session_state["auth_view"] = "reset"
                st.rerun()


def render_reset_password_page():
    """Render the reset password page."""
    from utils.auth import reset_password_with_token
    from utils.validators import validate_password

    st.markdown(
        """
<div style="text-align:center;padding:40px 0 20px;">
  <div style="font-size:2rem;font-weight:800;">Reset Password 🔒</div>
  <div style="color:#8B92A9;margin-top:6px;">Enter your token and new password.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        demo_token = st.session_state.get("_reset_token_demo", "")

        with st.form("reset_form"):
            token     = st.text_input("🔑 Reset Token", value=demo_token, placeholder="Paste your reset token")
            password  = st.text_input("🔒 New Password",     type="password")
            password2 = st.text_input("🔒 Confirm Password", type="password")
            submitted = st.form_submit_button("Reset Password →", use_container_width=True, type="primary")

            if submitted:
                errors = []
                if not token.strip():
                    errors.append("Reset token is required.")
                ok, msg = validate_password(password)
                if not ok:
                    errors.append(msg)
                if password != password2:
                    errors.append("Passwords do not match.")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    success, message = reset_password_with_token(token.strip(), password)
                    if success:
                        st.success("✅ Password reset! Please sign in with your new password.")
                        st.session_state["auth_view"] = "login"
                        st.session_state.pop("_reset_token_demo", None)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

        if st.button("← Back to Login", key="reset_back"):
            st.session_state["auth_view"] = "login"
            st.rerun()


# ─── Page Dispatcher ─────────────────────────────────────────────────────────

def dispatch_page(page: str):
    """Import and render the requested page module."""
    if not has_permission(page):
        st.error("🚫 Access Denied - You don't have permission to view this page.")
        st.stop()

    try:
        if page == "dashboard":
            from views.dashboard import render
        elif page == "analytics":
            from views.analytics import render
        elif page == "inventory":
            from views.inventory import render
        elif page == "categories":
            from views.categories import render
        elif page == "brands":
            from views.brands import render
        elif page == "suppliers":
            from views.suppliers import render
        elif page == "customers":
            from views.customers import render
        elif page == "purchases":
            from views.purchases import render
        elif page == "sales":
            from views.sales import render
        elif page == "stock_management":
            from views.stock_management import render
        elif page == "reports":
            from views.reports import render
        elif page == "user_management":
            from views.user_management import render
        elif page == "notifications":
            from views.notifications import render
        elif page == "export_center":
            from views.export_center import render
        elif page == "settings":
            from views.settings import render
        elif page == "profile":
            from views.profile import render
        else:
            from views.dashboard import render

        render()

    except ImportError as exc:
        st.error(f"Import failed: {exc}")
        st.exception(exc)
    except Exception as exc:
        st.error(f"❌ An error occurred loading `{page}`: {exc}")
        st.exception(exc)


# ─── Main App Router ──────────────────────────────────────────────────────────

def main():
    """Top-level router - auth check → sidebar → page dispatch."""

    # DB connectivity check
    db_status, db_msg = _db_ok()
    if not db_status:
        st.error(
            "⚠️ **Database not connected.**\n\n"
            f"**Error Details:** `{db_msg}`\n\n"
            "Please ensure your Streamlit Secrets (or `.env`) are configured correctly."
        )
        st.stop()
    else:
        # DB connected! Let's make sure tables exist and are seeded (Auto-Migration for Cloud)
        from database.connection import fetch_scalar
        try:
            # Check if users table actually has data
            count = fetch_scalar("SELECT COUNT(*) FROM users")
            if count == 0:
                raise Exception("Users table is empty!")
        except Exception as startup_err:
            # Table doesn't exist or is empty, run auto-migration!
            try:
                with st.spinner("Setting up cloud database tables for the first time..."):
                    from database.migrations import run_migration
                    run_migration()
                    st.success("✅ Cloud Database Initialized Successfully! Reloading...")
                    import time; time.sleep(2)
                    st.rerun()
            except Exception as migration_err:
                st.error(f"**Migration Failed:** {str(migration_err)}")
                st.stop()

    # AUTH ROUTING
    if not is_authenticated():
        # Hide sidebar on auth pages
        st.markdown(
            "<style>[data-testid='stSidebar']{display:none!important;}</style>",
            unsafe_allow_html=True,
        )
        view = st.session_state.get("auth_view", "login")
        if view == "login":
            render_login_page()
        elif view == "register":
            render_register_page()
        elif view == "forgot":
            render_forgot_password_page()
        elif view == "reset":
            render_reset_password_page()
        return

    # AUTHENTICATED - render native sidebar + page
    render_sidebar()
    current_page = st.session_state.get("current_page", "dashboard")
    dispatch_page(current_page)


if __name__ == "__main__":
    main()
