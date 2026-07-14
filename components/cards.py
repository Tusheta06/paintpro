"""
PaintPro Inventory Management System
=====================================
KPI Cards Component  |  components/cards.py

Functions to render beautiful dashboard metric cards with
HTML/CSS, delta indicators, and icons.
"""

import streamlit as st
from utils.formatting import format_currency, format_number

def render_kpi_card(
    title: str,
    value: str | float | int,
    icon: str,
    delta: str = None,
    delta_type: str = "up",
    is_currency: bool = False,
    is_number: bool = False
):
    """
    Render a modern KPI card.
    
    Args:
        title: Card label (e.g. 'Total Sales')
        value: Main metric value
        icon: Font Awesome icon class (e.g. 'fa-solid fa-cart-shopping')
        delta: Optional secondary metric/text (e.g. '+12% this week')
        delta_type: 'up' (green), 'down' (red), or 'neutral' (gray)
        is_currency: If True, formats value as currency
        is_number: If True, formats value with commas
    """
    
    # Format the value if needed
    display_value = value
    if is_currency:
        display_value = format_currency(value)
    elif is_number:
        display_value = format_number(value, decimals=0)
        
    # Delta styling
    delta_html = ""
    if delta:
        delta_class = f"kpi-delta-{delta_type}" if delta_type in ["up", "down"] else "kpi-delta-neutral"
        delta_icon = ""
        if delta_type == "up":
            delta_icon = '<i class="fa-solid fa-arrow-trend-up"></i>'
        elif delta_type == "down":
            delta_icon = '<i class="fa-solid fa-arrow-trend-down"></i>'
            
        delta_html = f'<div class="kpi-card-sub {delta_class}">{delta_icon} {delta}</div>'

    html = f"""
<div class="kpi-card">
    <div class="kpi-card-header">
        <div class="kpi-card-label">{title}</div>
        <div class="kpi-card-icon" style="background: rgba(108, 99, 255, 0.1); color: var(--primary);">
            <i class="{icon}"></i>
        </div>
    </div>
    <div class="kpi-card-value">{display_value}</div>
    {delta_html}
</div>
"""
    
    st.markdown(html, unsafe_allow_html=True)

def render_glass_card(title: str, content: str, icon: str = None):
    """Render a glassmorphism style card for special highlights."""
    icon_html = f'<i class="{icon}" style="margin-right: 8px; color: var(--primary);"></i>' if icon else ''
    
    html = f"""
<div class="glass-card" style="padding: 24px; height: 100%;">
    <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 12px; color: var(--text);">
        {icon_html}{title}
    </div>
    <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
        {content}
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
