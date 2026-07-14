"""
PaintPro Inventory Management System
=====================================
Dashboard Page  |  pages/dashboard.py

Displays top-level KPIs, charts, and recent activity.
"""

import streamlit as st
import pandas as pd

from database.connection import execute_one, execute_query
from utils.auth import require_auth
from utils.formatting import get_stock_badge_html, timeago, get_payment_badge_html
from components.cards import render_kpi_card, render_glass_card
from components.charts import render_revenue_trend, render_sales_by_category

def _load_kpis() -> dict:
    """Fetch dashboard KPIs from the database view."""
    return execute_one("SELECT * FROM vw_dashboard_kpis") or {}

def _load_recent_sales() -> list[dict]:
    """Fetch last 5 sales for the activity feed."""
    return execute_query(
        """
        SELECT id, invoice_number, customer_name, grand_total, payment_status, invoice_date
        FROM vw_sales_summary
        ORDER BY invoice_date DESC
        LIMIT 5
        """
    )

def _load_low_stock() -> list[dict]:
    """Fetch items currently low or out of stock."""
    return execute_query(
        """
        SELECT id, sku, name, current_stock, minimum_stock, stock_status 
        FROM vw_product_summary 
        WHERE stock_status IN ('low_stock', 'out_of_stock') 
        ORDER BY current_stock ASC 
        LIMIT 5
        """
    )

def _load_revenue_data() -> pd.DataFrame:
    """Fetch revenue data for the chart (last 7 days for demo)."""
    rows = execute_query(
        """
        SELECT invoice_date as Date, SUM(grand_total) as Revenue 
        FROM sales 
        WHERE status != 'cancelled' 
        GROUP BY invoice_date 
        ORDER BY invoice_date ASC 
        LIMIT 7
        """
    )
    return pd.DataFrame(rows)

def render():
    """Render the dashboard layout."""
    require_auth()

    # Navbar/Header
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Dashboard Overview</div>
    <div class="navbar-actions">
        <a href="#" class="navbar-icon-btn">
            <i class="fa-solid fa-bell"></i>
        </a>
    </div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    # ─── Load Data ───────────────────────────────────────────────────────────
    kpis = _load_kpis()
    
    # ─── Top KPI Row ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><div class="section-title">Key Metrics</div></div>', unsafe_allow_html=True)
    
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        render_kpi_card(
            title="Today's Revenue", 
            value=kpis.get("today_revenue", 0), 
            icon="fa-solid fa-indian-rupee-sign", 
            delta="Today", 
            delta_type="up", 
            is_currency=True
        )
    with kpi_cols[1]:
        render_kpi_card(
            title="Monthly Revenue", 
            value=kpis.get("monthly_revenue", 0), 
            icon="fa-solid fa-chart-pie", 
            delta="This Month", 
            delta_type="neutral", 
            is_currency=True
        )
    with kpi_cols[2]:
        render_kpi_card(
            title="Total Sales", 
            value=kpis.get("total_sales", 0), 
            icon="fa-solid fa-file-invoice", 
            delta="All Time", 
            delta_type="neutral", 
            is_number=True
        )
    with kpi_cols[3]:
        out_of_stock = kpis.get("out_of_stock_count", 0)
        render_kpi_card(
            title="Out of Stock", 
            value=out_of_stock, 
            icon="fa-solid fa-triangle-exclamation", 
            delta="Action required" if out_of_stock > 0 else "All good", 
            delta_type="down" if out_of_stock > 0 else "up", 
            is_number=True
        )
        
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # ─── Charts Row ──────────────────────────────────────────────────────────
    chart_col, info_col = st.columns([2, 1], gap="large")
    
    with chart_col:
        st.markdown('<div class="section-header"><div class="section-title">Revenue Trend</div></div>', unsafe_allow_html=True)
        df_rev = _load_revenue_data()
        fig_rev = render_revenue_trend(df_rev, "Date", "Revenue", "")
        st.plotly_chart(fig_rev, use_container_width=True, config={'displayModeBar': False})
        
    with info_col:
        st.markdown('<div class="section-header"><div class="section-title">Inventory Value</div></div>', unsafe_allow_html=True)
        val = kpis.get("inventory_value", 0)
        render_glass_card(
            title="Total Stock Value",
            content=f"<div style='font-size:2.2rem;font-weight:800;color:var(--text);margin-top:10px;'>₹{val:,.0f}</div><div style='margin-top:10px;font-size:0.85rem;'>Total cost price of all active products currently in stock.</div>",
            icon="fa-solid fa-boxes-stacked"
        )
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        render_glass_card(
            title="Catalog Size",
            content=f"You are managing <b>{kpis.get('total_products',0)}</b> products across <b>{kpis.get('total_categories',0)}</b> categories and <b>{kpis.get('total_brands',0)}</b> brands.",
            icon="fa-solid fa-tags"
        )

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    # ─── Tables Row (Recent Sales & Low Stock) ───────────────────────────────
    t_col1, t_col2 = st.columns([1, 1], gap="large")
    
    with t_col1:
        st.markdown('<div class="section-header"><div class="section-title">Recent Sales</div></div>', unsafe_allow_html=True)
        sales = _load_recent_sales()
        if not sales:
            st.info("No recent sales found.")
        else:
            rows_html = ""
            for s in sales:
                badge = get_payment_badge_html(s['payment_status'])
                when = timeago(s['invoice_date'])
                rows_html += f"""
<tr>
    <td><b>{s['invoice_number']}</b><br><small style="color:var(--text-muted);">{when}</small></td>
    <td>{s['customer_name']}</td>
    <td style="font-weight:bold;">₹{float(s['grand_total']):,.2f}</td>
    <td>{badge}</td>
</tr>
"""
            st.markdown(
                f"""
<div class="paintpro-table-wrapper">
  <table class="paintpro-table">
    <thead><tr><th>Invoice</th><th>Customer</th><th>Amount</th><th>Status</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""",
                unsafe_allow_html=True
            )
            
    with t_col2:
        st.markdown('<div class="section-header"><div class="section-title">Low Stock Alerts</div></div>', unsafe_allow_html=True)
        low_stock = _load_low_stock()
        if not low_stock:
            st.markdown(
                '<div class="alert-banner alert-success"><i class="fa-solid fa-circle-check alert-icon"></i><div class="alert-message">All items are well stocked!</div></div>', 
                unsafe_allow_html=True
            )
        else:
            rows_html = ""
            for p in low_stock:
                badge = get_stock_badge_html(p['current_stock'], p['minimum_stock'])
                rows_html += f"""
<tr>
    <td><small style="color:var(--text-muted);">{p['sku']}</small><br><b>{p['name']}</b></td>
    <td style="text-align:right;font-weight:bold;">{float(p['current_stock']):g}</td>
    <td>{badge}</td>
</tr>
"""
            st.markdown(
                f"""
<div class="paintpro-table-wrapper">
  <table class="paintpro-table">
    <thead><tr><th>Product</th><th style="text-align:right;">Stock</th><th>Status</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""",
                unsafe_allow_html=True
            )
            
    st.markdown("</div>", unsafe_allow_html=True) # End padding
