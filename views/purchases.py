"""
PaintPro Inventory Management System
=====================================
Purchases Page  |  pages/purchases.py

Manage purchase orders, receive stock, and track supplier payments.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.auth import require_auth, get_current_user
from utils.formatting import format_currency, format_date, get_payment_badge_html
from models.purchase import PurchaseModel
from database.connection import execute_query

# ─── Reference Data ───────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def _load_suppliers() -> dict:
    rows = execute_query("SELECT id, name FROM suppliers WHERE is_active=1 ORDER BY name")
    return {r["name"]: r["id"] for r in rows}

@st.cache_data(ttl=60)
def _load_products() -> dict:
    rows = execute_query("SELECT id, name, sku, cost_price FROM products WHERE is_active=1 ORDER BY name")
    return {f"{r['sku']} - {r['name']}": r for r in rows}

# ─── Dialogs ──────────────────────────────────────────────────────────────────

@st.dialog("View Purchase Order", width="large")
def _view_po_dialog(purchase_id: int):
    po = PurchaseModel.get_by_id(purchase_id)
    items = PurchaseModel.get_items(purchase_id)
    print("PURCHASE ITEMS DEBUG:", items)
    
    if not po:
        st.error("Purchase Order not found.")
        return
        
    st.markdown(f"### Purchase Order {po['po_number']}")
    
    # Header Info
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Supplier:**<br>{po['supplier_name']}", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**Date:**<br>{format_date(po['order_date'])}", unsafe_allow_html=True)
    with c3:
        st.markdown(f"**Status:**<br>{po['status'].upper()}", unsafe_allow_html=True)
        
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Items Table
    rows_html = ""
    for item in items:
        rows_html += f"""
<tr>
    <td><small>{item['sku']}</small><br><b>{item['product_name']}</b></td>
    <td style="text-align:right;">{float(item['quantity']):g}</td>
    <td style="text-align:right;">{format_currency(item['unit_cost'])}</td>
    <td style="text-align:right;font-weight:bold;">{format_currency(item.get('total_cost', item.get('line_total', 0)))}</td>
</tr>
"""
        
    st.markdown(
        f"""
<table class="paintpro-table" style="width:100%;margin-bottom:20px;">
    <thead style="background:var(--bg-secondary);">
        <tr>
            <th>Item</th>
            <th style="text-align:right;">Qty</th>
            <th style="text-align:right;">Unit Cost</th>
            <th style="text-align:right;">Total</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
""", 
        unsafe_allow_html=True
    )
    
    # Totals
    st.markdown(
        f"""
<div style="display:flex;justify-content:flex-end;width:100%;">
    <div style="width:300px;background:var(--bg-card);padding:16px;border-radius:var(--radius-sm);border:1px solid var(--border);">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="color:var(--text-muted);">Subtotal</span>
            <span>{format_currency(po['subtotal'])}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
            <span style="color:var(--text-muted);">GST</span>
            <span>{format_currency(po.get('gst_amount', 0))}</span>
        </div>
        <div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding-top:12px;font-weight:bold;font-size:1.1rem;color:var(--primary-light);">
            <span>Grand Total</span>
            <span>{format_currency(po['grand_total'])}</span>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Update Status Form
    if po['status'] != 'received':
        with st.form(f"update_status_{purchase_id}"):
            st.markdown("#### Update Order Status")
            st.info("Marking an order as 'received' will automatically increment the inventory stock.")
            uc1, uc2 = st.columns(2)
            with uc1:
                new_status = st.selectbox("Order Status", options=["draft", "ordered", "received", "cancelled"], index=["draft", "ordered", "received", "cancelled"].index(po['status']))
            with uc2:
                payment_status = st.selectbox(
                    "Payment Status",
                    options=["unpaid", "partial", "paid"],
                    index=["unpaid", "partial", "paid"].index(po["payment_status"])
                )
                
            if st.form_submit_button("Update Status", type="primary"):
                ok, msg = PurchaseModel.update_status(purchase_id, new_status, payment_status, get_current_user()['id'])
                if ok:
                    st.success("Status updated!")
                    st.session_state["_refresh_trigger"] = True
                    st.rerun()
                else:
                    st.error(f"Error: {msg}")


# ─── New Purchase Form (Stateful) ─────────────────────────────────────────────

def render_new_purchase_form():
    st.markdown("### Create Purchase Order")
    
    suppliers = _load_suppliers()
    products = _load_products()
    
    if not suppliers:
        st.warning("Please add at least one supplier before creating a purchase order.")
        if st.button("← Back"):
            st.session_state['purchase_view'] = 'list'
            st.rerun()
        return
        
    if not products:
        st.warning("Please add products to your inventory first.")
        if st.button("← Back"):
            st.session_state['purchase_view'] = 'list'
            st.rerun()
        return

    # Initialize Cart
    if "po_cart" not in st.session_state:
        st.session_state["po_cart"] = []

    # Supplier Selection
    col1, col2 = st.columns(2)
    with col1:
        sel_supp = st.selectbox("Select Supplier *", options=["Select"] + list(suppliers.keys()))
    with col2:
        exp_date = st.date_input("Expected Delivery Date")

    st.markdown("#### Add Items")
    
    # Add Item Form
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1:
            sel_prod = st.selectbox("Product", options=["Select"] + list(products.keys()), key="po_sel_prod")
        with c2:
            qty = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0, key="po_qty")
        with c3:
            # Auto-fill cost price if product selected
            default_cost = 0.0
            if sel_prod != "Select":
                default_cost = float(products[sel_prod]['cost_price'])
            unit_cost = st.number_input("Unit Cost (₹)", min_value=0.0, value=default_cost, key="po_unit_cost")
        with c4:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if st.button("Add to Order", type="primary", use_container_width=True):
                if sel_prod == "Select":
                    st.error("Select a product")
                else:
                    prod_info = products[sel_prod]
                    item = {
                        "product_id": prod_info['id'],
                        "name": prod_info['name'],
                        "sku": prod_info['sku'],
                        "quantity": qty,
                        "unit_cost": unit_cost,
                        "total_cost": qty * unit_cost
                    }
                    st.session_state["po_cart"].append(item)
                    st.rerun()
                    
    # Display Cart
    if st.session_state["po_cart"]:
        st.markdown("#### Order Summary")
        
        cart_df = pd.DataFrame(st.session_state["po_cart"])
        
        # Display as table
        rows_html = ""
        subtotal = 0.0
        for idx, row in cart_df.iterrows():
            subtotal += row['total_cost']
            rows_html += f"""
<tr>
    <td>{row['sku']} - {row['name']}</td>
    <td style="text-align:right;">{row['quantity']}</td>
    <td style="text-align:right;">{format_currency(row['unit_cost'])}</td>
    <td style="text-align:right;font-weight:bold;">{format_currency(row['total_cost'])}</td>
    <td style="text-align:center;">
        <button onclick="parent.postMessage({{type:'st_btn',key:'po_del_{idx}'}}, '*')" style="border:none;background:none;color:var(--danger);cursor:pointer;"><i class="fa-solid fa-trash"></i></button>
    </td>
</tr>
"""
            
        st.markdown(
            f"""
<table class="paintpro-table" style="width:100%;">
    <thead style="background:var(--bg-secondary);">
        <tr><th>Item</th><th style="text-align:right;">Qty</th><th style="text-align:right;">Cost</th><th style="text-align:right;">Total</th><th></th></tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
""", 
            unsafe_allow_html=True
        )
        
        # We need a fallback for deleting items since Streamlit buttons in raw HTML are tricky.
        # Let's use standard st.columns for the cart items so buttons work seamlessly.
        
        st.markdown("---")
        st.markdown("##### Edit/Remove Items")
        for idx, row in enumerate(st.session_state["po_cart"]):
            cc1, cc2 = st.columns([5, 1])
            with cc1:
                st.markdown(f"**{row['name']}** (Qty: {row['quantity']} @ {format_currency(row['unit_cost'])}) = **{format_currency(row['total_cost'])}**")
            with cc2:
                if st.button("Remove", key=f"btn_rem_{idx}", use_container_width=True):
                    st.session_state["po_cart"].pop(idx)
                    st.rerun()
                    
        # Tax and Totals
        tax_rate = st.selectbox("Apply Global Tax %", options=[0, 5, 12, 18, 28], index=3)
        tax_total = subtotal * (tax_rate / 100)
        grand_total = subtotal + tax_total
        
        st.markdown(
            f"""
<div style="background:var(--bg-card);padding:16px;border-radius:8px;border:1px solid var(--border);margin-top:20px;">
    <h4>Total: {format_currency(grand_total)}</h4>
    <small>Subtotal: {format_currency(subtotal)} | Tax: {format_currency(tax_total)}</small>
</div>
""", unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fc1, fc2, fc3 = st.columns([1, 1, 2])
        with fc1:
            if st.button("Cancel Order", use_container_width=True):
                st.session_state["po_cart"] = []
                st.session_state['purchase_view'] = 'list'
                st.rerun()
        with fc3:
            if st.button("Submit Purchase Order", type="primary", use_container_width=True):
                if sel_supp == "Select":
                    st.error("Please select a supplier.")
                else:
                    header = {
                        "supplier_id": suppliers[sel_supp],
                        "order_date": datetime.now().date(),
                        "expected_date": exp_date,
                        "status": "ordered",
                        "payment_status": "unpaid",
                        "subtotal": subtotal,
                        "discount_amount": 0,
                        "gst_amount": tax_total,
                        "shipping_cost": 0,
                        "grand_total": grand_total
                    }
                    
                    ok, msg = PurchaseModel.create_with_items(header, st.session_state["po_cart"], get_current_user()['id'])
                    if ok:
                        st.success(f"Purchase Order created successfully!")
                        st.session_state["po_cart"] = []
                        st.session_state['purchase_view'] = 'list'
                        st.rerun()
                    else:
                        st.error(f"Failed to create: {msg}")

# ─── Main Render ──────────────────────────────────────────────────────────────

def render():
    require_auth()

    # Navbar
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Purchases (Inbound)</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    if "purchase_view" not in st.session_state:
        st.session_state["purchase_view"] = "list"
        
    if st.session_state["purchase_view"] == "add":
        render_new_purchase_form()
    else:
        # ─── Toolbar ──────────────────────────────────────────────────────────
        t_col1, t_col2, t_col3 = st.columns([2, 1, 1], gap="medium")
        with t_col1:
            search = st.text_input("🔍 Search POs", placeholder="Search by PO number or supplier...", label_visibility="collapsed")
        with t_col2:
            filter_status = st.selectbox("Filter Status", options=["All", "ordered", "received", "cancelled", "draft"], label_visibility="collapsed")
        with t_col3:
            if st.button("➕ Create PO", use_container_width=True, type="primary"):
                st.session_state["purchase_view"] = "add"
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ─── Fetch Data ───────────────────────────────────────────────────────
        pos = PurchaseModel.get_all(search_query=search, status=filter_status)
        
        if not pos:
            st.markdown(
                """
<div class="empty-state">
  <div class="empty-state-icon">🛒</div>
  <div class="empty-state-title">No purchases found</div>
  <div class="empty-state-desc">Create a new purchase order to restock inventory.</div>
</div>
""", 
                unsafe_allow_html=True
            )
        else:
            # ─── Render View ──────────────────────────────────────────────────
            rows_html = ""
            for p in pos:
                status_colors = {
                    "received": "#00D4AA",
                    "ordered": "#FFB703",
                    "draft": "#8B92A9",
                    "cancelled": "#FF4757"
                }
                sc = status_colors.get(p['status'], "#8B92A9")
                status_badge = f"<span style='background:{sc}22;color:{sc};padding:2px 8px;border-radius:20px;font-size:0.7rem;font-weight:700;text-transform:uppercase;'>{p['status']}</span>"
                
                pay_badge = get_payment_badge_html(p['payment_status'])
                date_str = format_date(p['order_date'])
                
                rows_html += f"""
<tr>
    <td><b>{p['po_number']}</b><br><small style="color:var(--text-muted);">{date_str}</small></td>
    <td>{p['supplier_name']}</td>
    <td style="text-align:right;font-weight:bold;">{format_currency(p['grand_total'])}</td>
    <td>{status_badge}</td>
    <td>{pay_badge}</td>
    <td><span style="color:var(--text-muted);font-size:0.75rem;">See actions below</span></td>
</tr>
"""
                
            st.markdown(
                f"""
<div class="paintpro-table-wrapper" style="margin-bottom: 20px;">
    <table class="paintpro-table">
        <thead>
            <tr>
                <th>PO Number</th>
                <th>Supplier</th>
                <th style="text-align:right;">Amount</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
""", 
                unsafe_allow_html=True
            )

            # Interactive Action Grid
            st.markdown("#### Quick Actions")
            cols_per_row = 4
            for i in range(0, len(pos), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(pos):
                        p = pos[i + j]
                        with cols[j]:
                            st.markdown(f"**{p['po_number']}**")
                            if st.button("👁️ View / Receive", key=f"view_{p['id']}", use_container_width=True):
                                _view_po_dialog(p['id'])
                            st.markdown("<br>", unsafe_allow_html=True)
                        
    st.markdown("</div>", unsafe_allow_html=True)
