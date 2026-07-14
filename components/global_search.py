"""
PaintPro Inventory Management System
=====================================
Global Search Component  |  components/global_search.py

Searches across Products, Customers, Suppliers, and Sales.
"""

import streamlit as st
import pandas as pd
from database.connection import execute_query
from utils.formatting import format_currency

@st.dialog("🔍 Global Search Results", width="large")
def global_search_dialog(query: str):
    if not query or len(query) < 2:
        st.warning("Please enter at least 2 characters to search.")
        return
        
    st.markdown(f"Results for **'{query}'**")
    
    val = f"%{query}%"
    
    with st.spinner("Searching database..."):
        # 1. Search Products
        prods = execute_query(
            "SELECT sku, name, current_stock, selling_price FROM products WHERE (name LIKE %s OR sku LIKE %s) AND is_active=1", 
            (val, val)
        )
        
        # 2. Search Customers
        custs = execute_query(
            "SELECT name, phone, customer_type FROM customers WHERE (name LIKE %s OR phone LIKE %s) AND is_active=1", 
            (val, val)
        )
        
        # 3. Search Suppliers
        supps = execute_query(
            "SELECT name, phone, gst_number FROM suppliers WHERE (name LIKE %s OR gst_number LIKE %s) AND is_active=1", 
            (val, val)
        )
        
        # 4. Search Sales (Invoices)
        sales = execute_query(
            "SELECT invoice_number, invoice_date, grand_total, status FROM sales WHERE invoice_number LIKE %s", 
            (val,)
        )
        
    t1, t2, t3, t4 = st.tabs([
        f"Products ({len(prods)})", 
        f"Customers ({len(custs)})", 
        f"Suppliers ({len(supps)})", 
        f"Invoices ({len(sales)})"
    ])
    
    with t1:
        if prods:
            df = pd.DataFrame(prods)
            df.columns = ["SKU", "Product Name", "Stock", "Price"]
            df["Price"] = df["Price"].apply(lambda x: format_currency(x))
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No matching products found.")
            
    with t2:
        if custs:
            df = pd.DataFrame(custs)
            df.columns = ["Customer Name", "Phone", "Type"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No matching customers found.")
            
    with t3:
        if supps:
            df = pd.DataFrame(supps)
            df.columns = ["Supplier Name", "Phone", "GSTIN"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No matching suppliers found.")
            
    with t4:
        if sales:
            df = pd.DataFrame(sales)
            df.columns = ["Invoice #", "Date", "Total", "Status"]
            df["Total"] = df["Total"].apply(lambda x: format_currency(x))
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No matching invoices found.")
