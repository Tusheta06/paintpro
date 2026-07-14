"""
PaintPro Inventory Management System
=====================================
Reports Page  |  pages/reports.py

Generate, view, and export tabular reports for sales, purchases,
inventory valuation, and low stock alerts.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

from utils.auth import require_auth
from utils.formatting import format_currency
from database.connection import execute_query

# ─── Report Generators ────────────────────────────────────────────────────────

def _generate_sales_report(start_date: date, end_date: date) -> pd.DataFrame:
    sql = """
        SELECT
            invoice_number AS 'Invoice #',
            DATE(invoice_date) AS 'Date',
            customer_name AS 'Customer',
            status AS 'Order Status',
            payment_status AS 'Payment Status',
            subtotal AS 'Subtotal (₹)',
            gst_amount AS 'Tax (₹)',
            discount_amount AS 'Discount (₹)',
            grand_total AS 'Grand Total (₹)'
        FROM sales
        WHERE DATE(invoice_date) BETWEEN %s AND %s
        ORDER BY invoice_date DESC
    """
    rows = execute_query(sql, (start_date, end_date))
    return pd.DataFrame(rows)

def _generate_purchases_report(start_date: date, end_date: date) -> pd.DataFrame:
    sql = """
        SELECT
            p.po_number AS 'PO #',
            DATE(p.order_date) AS 'Date',
            s.name AS 'Supplier',
            p.status AS 'Status',
            p.payment_status AS 'Payment Status',
            p.subtotal AS 'Subtotal (₹)',
            p.gst_amount AS 'Tax (₹)',
            p.discount_amount AS 'Discount (₹)',
            p.grand_total AS 'Grand Total (₹)'
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE DATE(p.order_date) BETWEEN %s AND %s
        ORDER BY p.order_date DESC
    """
    rows = execute_query(sql, (start_date, end_date))
    return pd.DataFrame(rows)

def _generate_inventory_valuation() -> pd.DataFrame:
    sql = """
        SELECT
            p.sku AS 'SKU',
            p.name AS 'Product Name',
            c.name AS 'Category',
            p.current_stock AS 'Qty in Stock',
            p.cost_price AS 'Unit Cost (₹)',
            p.selling_price AS 'Unit Price (₹)',
            (p.current_stock * p.cost_price) AS 'Total Cost Value (₹)'
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.current_stock > 0
        ORDER BY (p.current_stock * p.cost_price) DESC
    """
    rows = execute_query(sql)
    return pd.DataFrame(rows)

def _generate_low_stock_report() -> pd.DataFrame:
    sql = """
        SELECT sku as 'SKU',
               name as 'Product Name',
               category_name as 'Category',
               brand_name as 'Brand',
               current_stock as 'Current Stock',
               minimum_stock as 'Min Threshold',
               stock_status as 'Status'
        FROM vw_product_summary
        WHERE stock_status IN ('low_stock', 'out_of_stock')
        ORDER BY current_stock ASC
    """
    rows = execute_query(sql)
    return pd.DataFrame(rows)

# ─── Main Render ──────────────────────────────────────────────────────────────

def render():
    require_auth()

    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Reports & Analytics</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    st.markdown("### Generate Report")
    
    # ─── Configuration ────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 2])
    
    with col1:
        report_type = st.radio(
            "Select Report Type",
            [
                "Sales Report", 
                "Purchases Report", 
                "Inventory Valuation", 
                "Low Stock Alerts"
            ]
        )
        
    with col2:
        if report_type in ["Sales Report", "Purchases Report"]:
            st.markdown("**Date Range Filters**")
            d1, d2 = st.columns(2)
            with d1:
                start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
            with d2:
                end_date = st.date_input("End Date", value=date.today())
        else:
            st.info("This report generates a current real-time snapshot. No date filters required.")
            start_date, end_date = None, None

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── Data Fetching & Display ──────────────────────────────────────────────
    
    with st.spinner("Generating Report..."):
        df = pd.DataFrame()
        
        if report_type == "Sales Report":
            df = _generate_sales_report(start_date, end_date)
            title = f"Sales Report ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')})"
        elif report_type == "Purchases Report":
            df = _generate_purchases_report(start_date, end_date)
            title = f"Purchases Report ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')})"
        elif report_type == "Inventory Valuation":
            df = _generate_inventory_valuation()
            title = "Inventory Valuation Snapshot"
        elif report_type == "Low Stock Alerts":
            df = _generate_low_stock_report()
            title = "Low Stock & Out of Stock Alerts"

    # ─── Results View ─────────────────────────────────────────────────────────
    
    if df.empty:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">📄</div>
  <div class="empty-state-title">No data found</div>
  <div class="empty-state-desc">Try expanding your date range.</div>
</div>
""", 
            unsafe_allow_html=True
        )
    else:
        # Header & Export
        head_c1, head_c2 = st.columns([3, 1])
        with head_c1:
            st.markdown(f"#### {title}")
            st.caption(f"Showing {len(df)} records.")
        with head_c2:
            # CSV Download
            csv = df.to_csv(index=False).encode('utf-8')
            safe_title = title.replace(" ", "_").replace("(", "").replace(")", "")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{safe_title}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )

        # KPIs Summaries (if applicable)
        if report_type == "Sales Report":
            st.markdown(
                f"""
<div style="display:flex;gap:16px;margin-bottom:20px;">
    <div style="background:var(--bg-card);padding:12px 20px;border-radius:8px;border:1px solid var(--border);">
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;">Total Invoices</div>
        <div style="font-size:1.5rem;font-weight:bold;color:var(--text);">{len(df)}</div>
    </div>
    <div style="background:var(--bg-card);padding:12px 20px;border-radius:8px;border:1px solid var(--border);">
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;">Total Revenue</div>
        <div style="font-size:1.5rem;font-weight:bold;color:var(--primary-light);">{format_currency(df['Grand Total (₹)'].sum())}</div>
    </div>
</div>
""", unsafe_allow_html=True
            )
        elif report_type == "Inventory Valuation":
            st.markdown(
                f"""
<div style="display:flex;gap:16px;margin-bottom:20px;">
    <div style="background:var(--bg-card);padding:12px 20px;border-radius:8px;border:1px solid var(--border);">
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;">Total Stock Value</div>
        <div style="font-size:1.5rem;font-weight:bold;color:var(--primary-light);">{format_currency(df['Total Cost Value (₹)'].sum())}</div>
    </div>
</div>
""", unsafe_allow_html=True
            )

        # Data Table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
    st.markdown("</div>", unsafe_allow_html=True)
