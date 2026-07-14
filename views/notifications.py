"""
PaintPro Inventory Management System
=====================================
Notifications Page  |  pages/notifications.py

Displays system alerts and actionable tasks.
"""

import streamlit as st
from utils.auth import require_auth
from utils.notifications import get_system_notifications

def render():
    require_auth()

    # Navbar
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">System Notifications</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    with st.spinner("Fetching alerts..."):
        alerts = get_system_notifications()
        
    # Update session state badge count
    st.session_state["notification_count"] = len(alerts)
    
    if not alerts:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">🎉</div>
  <div class="empty-state-title">You're all caught up!</div>
  <div class="empty-state-desc">No new notifications or alerts at this time.</div>
</div>
""", 
            unsafe_allow_html=True
        )
        return
        
    st.markdown(f"**You have {len(alerts)} pending alerts requiring your attention.**")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Render notifications
    for idx, alert in enumerate(alerts):
        bg_color = {
            "danger": "rgba(255, 71, 87, 0.1)",
            "warning": "rgba(255, 183, 3, 0.1)",
            "info": "rgba(108, 99, 255, 0.1)"
        }.get(alert["type"], "rgba(139, 146, 169, 0.1)")
        
        icon_color = {
            "danger": "#FF4757",
            "warning": "#FFB703",
            "info": "#6C63FF"
        }.get(alert["type"], "#8B92A9")
        
        c1, c2 = st.columns([10, 2])
        with c1:
            st.markdown(
                f"""
<div style="background:{bg_color}; border-left: 4px solid {icon_color}; padding: 16px; border-radius: 4px; margin-bottom: 12px; display: flex; align-items: center; gap: 16px;">
    <div style="color:{icon_color}; font-size: 1.5rem;"><i class="fa-solid {alert['icon']}"></i></div>
    <div>
        <div style="font-weight: 700; color: var(--text);">{alert['title']}</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem;">{alert['message']}</div>
    </div>
</div>
""",
                unsafe_allow_html=True
            )
        with c2:
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.button("Take Action →", key=f"btn_action_{idx}", use_container_width=True):
                st.session_state["current_page"] = alert["action_link"]
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)
