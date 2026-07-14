"""
PaintPro Inventory Management System
=====================================
Export Center Page  |  pages/export_center.py

Allows secure, 1-click downloading of all major database tables 
into CSV format for backups and accounting.
"""

import streamlit as st
import pandas as pd
from datetime import date

from utils.auth import require_auth
from database.connection import execute_query

def _fetch_table_data(table_name: str) -> pd.DataFrame:
    """Fetch all rows from a given table safely."""
    # We whitelist tables to prevent SQL injection or accessing sensitive tables like `users`
    allowed_tables = {
        "Products": "SELECT * FROM products",
        "Categories": "SELECT * FROM categories",
        "Brands": "SELECT * FROM brands",
        "Customers": "SELECT * FROM customers",
        "Suppliers": "SELECT * FROM suppliers",
        "Sales (Invoices)": "SELECT * FROM sales",
        "Purchase Orders": "SELECT * FROM purchases",
        "Stock Audit Logs": "SELECT * FROM stock_logs",
    }
    
    if table_name not in allowed_tables:
        return pd.DataFrame()
        
    query = allowed_tables[table_name]
    rows = execute_query(query)
    
    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame()

def render():
    require_auth()

    # Navbar
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Data Export Center</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    st.markdown("### 📥 Database Backups & Export")
    st.markdown(
        "<div style='color:var(--text-muted);margin-bottom:24px;'>"
        "Securely export your PaintPro IMS data to CSV format. This is highly recommended for monthly accounting reconciliation and routine backups."
        "</div>",
        unsafe_allow_html=True
    )
    
    tables_to_export = [
        "Products", 
        "Categories", 
        "Brands", 
        "Customers", 
        "Suppliers", 
        "Sales (Invoices)", 
        "Purchase Orders",
        "Stock Audit Logs"
    ]
    
    st.info("💡 **Tip:** CSV files can be opened in Microsoft Excel, Google Sheets, or imported directly into accounting software like Tally or QuickBooks.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    cols_per_row = 2
    for i in range(0, len(tables_to_export), cols_per_row):
        cols = st.columns(cols_per_row, gap="large")
        for j in range(cols_per_row):
            if i + j < len(tables_to_export):
                table = tables_to_export[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"#### {table}")
                        
                        # Generate data dynamically when the user requests it
                        with st.spinner(f"Preparing {table} data..."):
                            df = _fetch_table_data(table)
                            
                        if df.empty:
                            st.warning(f"No records found in {table}.")
                        else:
                            st.caption(f"Ready for download ({len(df)} records found).")
                            
                            csv = df.to_csv(index=False).encode('utf-8')
                            file_name = f"paintpro_export_{table.lower().replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.csv"
                            
                            st.download_button(
                                label=f"Download {table} CSV",
                                data=csv,
                                file_name=file_name,
                                mime="text/csv",
                                use_container_width=True,
                                type="primary"
                            )
                            
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
