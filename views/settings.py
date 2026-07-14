"""
PaintPro Inventory Management System
=====================================
Settings Page  |  pages/settings.py

Admin-only configuration page to manage application settings,
company profile, and system preferences.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from config.settings import company_config, app_config, theme_config, upload_config

def render():
    require_auth()

    me = get_current_user()
    if me["role"] != "admin":
        st.error("🚫 Access Denied - Admin only.")
        return

    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Settings</div>
</div>
""",
        unsafe_allow_html=True
    )
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    st.caption("Manage company profile and system configuration.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🏢 Company Profile", "🛠️ System Preferences", "🎨 Appearance"])

    with tab1:
        st.markdown("### Company Information")
        st.markdown("<span style='color:var(--text-muted);font-size:0.85rem;'>These details appear on invoices and reports. Currently configured via environment variables.</span><br><br>", unsafe_allow_html=True)
        
        with st.form("company_profile_form"):
            name = st.text_input("Company Name *", value=company_config.NAME, disabled=True)
            address = st.text_area("Address", value=company_config.ADDRESS, disabled=True)
            
            c1, c2 = st.columns(2)
            phone = c1.text_input("Phone", value=company_config.PHONE, disabled=True)
            email = c2.text_input("Email", value=company_config.EMAIL, disabled=True)
            
            c3, c4 = st.columns(2)
            gst = c3.text_input("GSTIN", value=company_config.GST, disabled=True)
            website = c4.text_input("Website", value=company_config.WEBSITE, disabled=True)
            
            submit = st.form_submit_button("Save Changes (Disabled)", type="primary", disabled=True)
            
        st.info("To modify company details permanently, please update the `.env` file and restart the application.")

    with tab2:
        st.markdown("### Application Settings")
        
        c1, c2 = st.columns(2)
        c1.text_input("Application Name", value=app_config.NAME, disabled=True)
        c2.text_input("Version", value=app_config.VERSION, disabled=True)
        
        c3, c4 = st.columns(2)
        c3.text_input("Environment", value=app_config.ENV, disabled=True)
        c4.text_input("Session Timeout (Minutes)", value=str(app_config.SESSION_TIMEOUT_MINUTES), disabled=True)
        
        st.markdown("#### Upload Constraints")
        st.text_input("Max Image Size (MB)", value=str(upload_config.MAX_SIZE_MB), disabled=True)
        st.text_input("Allowed Types", value=", ".join(upload_config.ALLOWED_TYPES), disabled=True)
        
        st.toggle("Debug Mode Enabled", value=app_config.DEBUG, disabled=True)
        
    with tab3:
        st.markdown("### Appearance")
        st.color_picker("Primary Brand Color", value=theme_config.PRIMARY_COLOR, disabled=True)
        st.color_picker("Success Color", value=theme_config.SUCCESS_COLOR, disabled=True)
        st.color_picker("Warning Color", value=theme_config.WARNING_COLOR, disabled=True)
        st.color_picker("Danger Color", value=theme_config.DANGER_COLOR, disabled=True)
        
        st.info("Theme configuration is managed in `config/settings.py` and `assets/css/main.css`.")
    
    st.markdown("</div>", unsafe_allow_html=True)
