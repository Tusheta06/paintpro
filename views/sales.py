"""
PaintPro Inventory Management System
=====================================
Sales Page  |  pages/sales.py

Manage sales invoices (Point of Sale), deduct stock, and track customer billing.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

from utils.auth import require_auth, get_current_user
from utils.formatting import format_currency, format_date, get_payment_badge_html
from utils.pdf_generator import generate_sale_invoice_pdf
from models.sale import SaleModel
from database.connection import execute_query

# ─── Reference Data ───────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def _load_customers() -> dict:
    rows = execute_query("SELECT id, name, customer_type FROM customers WHERE is_active=1 ORDER BY name")
    return {f"{r['name']} ({r['customer_type']})": r["id"] for r in rows}

@st.cache_data(ttl=60)
def _load_products() -> dict:
    rows = execute_query("SELECT id, name, sku, selling_price, current_stock, gst_percentage FROM products WHERE is_active=1 AND current_stock > 0 ORDER BY name")
    return {f"{r['sku']} - {r['name']} (Stock: {r['current_stock']:g})": r for r in rows}

# ─── Dialogs ──────────────────────────────────────────────────────────────────

@st.dialog("View Sale Invoice", width="large")
def _view_sale_dialog(sale_id: int):
    sale = SaleModel.get_by_id(sale_id)
    items = SaleModel.get_items(sale_id)
    
    if not sale:
        st.error("Sale Record not found.")
        return
        
    st.markdown(f"### Invoice {sale['invoice_number']}")
    
    # Header Info
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Billed To:**<br>{sale['customer_name']}<br><small>{sale['customer_address'] or ''}</small>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**Invoice Date:**<br>{format_date(sale['invoice_date'])}<br>**Due Date:**<br>{format_date(sale['due_date'])}", unsafe_allow_html=True)
    with c3:
        st.markdown(f"**Payment Status:**<br>{sale['payment_status'].upper()}<br>**Order Status:**<br>{sale['status'].upper()}", unsafe_allow_html=True)
        
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Items Table
    rows_html = ""
    for item in items:
        disc = f"(-{format_currency(item['discount_amount'])})" if item.get('discount_amount', 0) > 0 else ""
        rows_html += f"""
<tr>
    <td><small>{item['sku']}</small><br><b>{item['product_name']}</b></td>
    <td style="text-align:right;">{float(item['quantity']):g}</td>
    <td style="text-align:right;">{format_currency(item['unit_price'])} {disc}</td>
    <td style="text-align:right;font-weight:bold;">{format_currency(item['line_total'])}</td>
</tr>
"""
        
    st.markdown(
        f"""
<table class="paintpro-table" style="width:100%;margin-bottom:20px;">
    <thead style="background:var(--bg-secondary);">
        <tr>
            <th>Item Description</th>
            <th style="text-align:right;">Qty</th>
            <th style="text-align:right;">Rate</th>
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
            <span>{format_currency(sale['subtotal'])}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;color:var(--danger);">
            <span>Discount</span>
            <span>-{format_currency(sale.get('discount_amount', 0))}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
            <span style="color:var(--text-muted);">Taxes</span>
            <span>{format_currency(sale.get('gst_amount', 0))}</span>
        </div>
        <div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding-top:12px;font-weight:bold;font-size:1.1rem;color:var(--primary-light);">
            <span>Grand Total</span>
            <span>{format_currency(sale['grand_total'])}</span>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Update Status Form
    with st.form(f"update_status_{sale_id}"):
        st.markdown("#### Update Invoice Status")
        uc1, uc2 = st.columns(2)
        with uc1:
           status_options = ["draft", "confirmed", "shipped", "delivered", "cancelled", "returned"]

        new_status = st.selectbox(
            "Order Status",
            options=status_options,
            index=status_options.index(sale['status']) if sale['status'] in status_options else 0
        )
        with uc2:
            payment_options = ["unpaid", "partial", "paid", "overdue", "cancelled", "refunded"]

        payment_status = st.selectbox(
            "Payment Status",
            options=payment_options,
            index=payment_options.index(sale['payment_status']) if sale['payment_status'] in payment_options else 0
        )
            
        if st.form_submit_button("Update Status", type="primary"):
            ok, msg = SaleModel.update_status(sale_id, new_status, payment_status, get_current_user()['id'])
            if ok:
                st.success("Status updated!")
                st.session_state["_refresh_trigger"] = True
                st.rerun()
            else:
                st.error(f"Error: {msg}")
                
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Export")
    pdf_bytes = generate_sale_invoice_pdf(sale, items)
    st.download_button(
        label="📄 Download PDF Invoice",
        data=pdf_bytes,
        file_name=f"{sale['invoice_number']}.pdf",
        mime="application/pdf",
        type="secondary",
        use_container_width=True
    )


# ─── New Sale Form (Stateful POS) ─────────────────────────────────────────────

def render_new_sale_form():
    st.markdown("### Point of Sale (New Invoice)")
    
    customers = _load_customers()
    products = _load_products()
    
    if not customers:
        st.warning("Please add at least one customer before creating a sale.")
        if st.button("← Back"):
            st.session_state['sale_view'] = 'list'
            st.rerun()
        return
        
    if not products:
        st.warning("No products with stock available.")
        if st.button("← Back"):
            st.session_state['sale_view'] = 'list'
            st.rerun()
        return

    # Initialize Cart
    if "sale_cart" not in st.session_state:
        st.session_state["sale_cart"] = []

    # Customer Selection
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_cust = st.selectbox("Select Customer *", options=["Select"] + list(customers.keys()))
    with col2:
        inv_date = st.date_input("Invoice Date", value=date.today())
    with col3:
        due_date = st.date_input("Due Date", value=date.today())

    st.markdown("#### Add Items to Cart")
    
    # Add Item Form
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1:
            sel_prod = st.selectbox("Product", options=["Select"] + list(products.keys()), key="sale_sel_prod")
        with c2:
            qty = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0, key="sale_qty")
        with c3:
            # Auto-fill selling price if product selected
            default_price = 0.0
            if sel_prod != "Select":
                default_price = float(products[sel_prod]['selling_price'])
            unit_price = st.number_input("Unit Price (₹)", min_value=0.0, value=default_price, key="sale_unit_price")
        with c4:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if st.button("Add to Cart", type="primary", use_container_width=True):
                if sel_prod == "Select":
                    st.error("Select a product")
                else:
                    prod_info = products[sel_prod]
                    if qty > prod_info['current_stock']:
                        st.error(f"Cannot add {qty}. Only {prod_info['current_stock']:g} in stock.")
                    else:
                        item = {
                            "product_id": prod_info['id'],
                            "name": prod_info['name'],
                            "sku": prod_info['sku'],
                            "gst_percentage": prod_info['gst_percentage'],
                            "quantity": qty,
                            "unit_price": unit_price,
                            "discount": 0.0, # Default discount
                            "total_price": qty * unit_price
                        }
                        st.session_state["sale_cart"].append(item)
                        st.rerun()
                    
    # Display Cart
    if st.session_state["sale_cart"]:
        st.markdown("#### Invoice Summary")
        
        cart_df = pd.DataFrame(st.session_state["sale_cart"])
        
        # Display as table
        rows_html = ""
        subtotal = 0.0
        tax_total = 0.0
        
        for idx, row in cart_df.iterrows():
            subtotal += row['total_price']
            # Calculate item tax based on product GST
            tax_total += row['total_price'] * (float(row['gst_percentage'] or 0) / 100.0)
            
            rows_html += f"""
<tr>
    <td>{row['sku']} - {row['name']}</td>
    <td style="text-align:right;">{row['quantity']}</td>
    <td style="text-align:right;">{format_currency(row['unit_price'])}</td>
    <td style="text-align:right;">{row['gst_percentage']}%</td>
    <td style="text-align:right;font-weight:bold;">{format_currency(row['total_price'])}</td>
</tr>
"""
            
        st.markdown(
            f"""
<table class="paintpro-table" style="width:100%;">
    <thead style="background:var(--bg-secondary);">
        <tr><th>Item</th><th style="text-align:right;">Qty</th><th style="text-align:right;">Rate</th><th style="text-align:right;">GST</th><th style="text-align:right;">Total</th></tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
""", 
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.markdown("##### Remove Items")
        for idx, row in enumerate(st.session_state["sale_cart"]):
            cc1, cc2 = st.columns([5, 1])
            with cc1:
                st.markdown(f"**{row['name']}** (Qty: {row['quantity']})")
            with cc2:
                if st.button("Remove", key=f"btn_rem_sale_{idx}", use_container_width=True):
                    st.session_state["sale_cart"].pop(idx)
                    st.rerun()
                    
        # Discounts and Totals
        global_discount = st.number_input("Global Discount (₹)", min_value=0.0, value=0.0)
        
        grand_total = subtotal + tax_total - global_discount
        
        st.markdown(
            f"""
<div style="background:var(--bg-card);padding:16px;border-radius:8px;border:1px solid var(--border);margin-top:20px;">
    <h4 style="color:var(--primary-light);">Amount Due: {format_currency(grand_total)}</h4>
    <small>Subtotal: {format_currency(subtotal)} | Tax: {format_currency(tax_total)} | Discount: {format_currency(global_discount)}</small>
</div>
""", unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fc1, fc2, fc3 = st.columns([1, 1, 2])
        with fc1:
            if st.button("Cancel Sale", use_container_width=True):
                st.session_state["sale_cart"] = []
                st.session_state['sale_view'] = 'list'
                st.rerun()
        with fc3:
            if st.button("Complete Sale (Deduct Stock)", type="primary", use_container_width=True):
                if sel_cust == "Select":
                    st.error("Please select a customer.")
                elif grand_total < 0:
                    st.error("Grand total cannot be negative.")
                else:
                    from datetime import datetime as _dt
                    inv_num = f"INV-{_dt.now().strftime('%Y%m%d%H%M%S')}"
                    header = {
                        "invoice_number": inv_num,
                        "customer_id": customers[sel_cust],
                        "invoice_date": inv_date,
                        "due_date": due_date,
                        "status": "confirmed",
                        "payment_status": "paid",
                        "subtotal": subtotal,
                        "gst_amount": tax_total,
                        "discount_amount": global_discount,
                        "grand_total": grand_total,
                        "paid_amount": grand_total,
                    }
                    
                    ok, msg = SaleModel.create_with_items(header, st.session_state["sale_cart"], get_current_user()['id'])
                    if ok:
                        st.success(f"Sale completed successfully! Stock has been deducted.")
                        st.session_state["sale_cart"] = []
                        st.session_state['sale_view'] = 'list'
                        st.rerun()
                    else:
                        st.error(f"Failed to create: {msg}")

# ─── Main Render ──────────────────────────────────────────────────────────────

def render():
    st.title("Sales")
    require_auth()

    # Navbar
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Sales (Point of Sale)</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    if "sale_view" not in st.session_state:
        st.session_state["sale_view"] = "list"
        
    if st.session_state["sale_view"] == "add":
        render_new_sale_form()
    else:
        # ─── Toolbar ──────────────────────────────────────────────────────────
        t_col1, t_col2, t_col3 = st.columns([2, 1, 1], gap="medium")
        with t_col1:
            search = st.text_input("🔍 Search Invoices", placeholder="Search by Invoice # or customer...", label_visibility="collapsed")
        with t_col2:
            filter_status = st.selectbox("Filter Status", options=["All", "completed", "cancelled", "draft"], label_visibility="collapsed")
        with t_col3:
            if st.button("➕ New Sale (POS)", use_container_width=True, type="primary"):
                st.session_state["sale_view"] = "add"
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ─── Fetch Data ───────────────────────────────────────────────────────
        sales = SaleModel.get_all(search_query=search, status=filter_status)
        
        if not sales:
            st.markdown(
                """
<div class="empty-state">
  <div class="empty-state-icon">💰</div>
  <div class="empty-state-title">No sales found</div>
  <div class="empty-state-desc">Create a new sale invoice to record a transaction.</div>
</div>
""", 
                unsafe_allow_html=True
            )
        else:
            # ─── Render View ──────────────────────────────────────────────────
            rows_html = ""
            for s in sales:
                status_colors = {
                    "completed": "#00D4AA",
                    "draft": "#8B92A9",
                    "cancelled": "#FF4757"
                }
                sc = status_colors.get(s['status'], "#8B92A9")
                status_badge = f"<span style='background:{sc}22;color:{sc};padding:2px 8px;border-radius:20px;font-size:0.7rem;font-weight:700;text-transform:uppercase;'>{s['status']}</span>"
                
                pay_badge = get_payment_badge_html(s['payment_status'])
                date_str = format_date(s['invoice_date'])
                
                rows_html += f"""
<tr>
    <td><b>{s['invoice_number']}</b><br><small style="color:var(--text-muted);">{date_str}</small></td>
    <td>{s['customer_name']}</td>
    <td style="text-align:right;font-weight:bold;color:var(--primary-light);">{format_currency(s['grand_total'])}</td>
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
                <th>Invoice #</th>
                <th>Customer</th>
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
            for i in range(0, len(sales), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(sales):
                        s = sales[i + j]
                        with cols[j]:
                            st.markdown(f"**{s['invoice_number']}**")
                            if st.button("👁️ View Invoice", key=f"view_{s['id']}", use_container_width=True):
                                _view_sale_dialog(s['id'])
                            st.markdown("<br>", unsafe_allow_html=True)
                        
    st.markdown("</div>", unsafe_allow_html=True)
