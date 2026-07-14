"""
PaintPro Inventory Management System
=====================================
Customers Page  |  pages/customers.py

Manage client relationships: view, add, edit, delete.
Supports tracking retail vs. contractor types.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.validators import validate_required, validate_email, validate_phone, validate_gst_number
from models.customer import CustomerModel
from config.constants import CUSTOMER_TYPES

# ─── Modal Dialogs ────────────────────────────────────────────────────────────

@st.dialog("Delete Customer")
def _delete_dialog(customer_id: int, customer_name: str):
    st.warning(f"Are you sure you want to delete the customer **{customer_name}**?")
    st.markdown("Customers with existing sales records cannot be deleted to preserve financial history.")
    
    col1, col2 = st.columns(2)
    if col1.button("Cancel", use_container_width=True):
        st.rerun()
    if col2.button("Yes, Delete", type="primary", use_container_width=True):
        ok, msg = CustomerModel.delete(customer_id, get_current_user()["id"])
        if ok:
            st.success("Customer deleted successfully!")
            st.session_state["_refresh_trigger"] = True
            st.rerun()
        else:
            st.error(f"Failed to delete: {msg}")

@st.dialog("Customer Form", width="large")
def _customer_form_dialog(customer_id: int = None):
    is_edit = customer_id is not None
    cust = {}
    if is_edit:
        cust = CustomerModel.get_by_id(customer_id)
        if not cust:
            st.error("Customer not found.")
            return

    st.markdown(f"### {'Edit' if is_edit else 'Add'} Customer")
    
    with st.form("customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer/Company Name *", value=cust.get("name", ""))
            ctype = st.selectbox("Customer Type", options=["Select"] + CUSTOMER_TYPES, index=(CUSTOMER_TYPES.index(cust.get("customer_type")) + 1) if cust.get("customer_type") in CUSTOMER_TYPES else 0)
        with col2:
            phone = st.text_input("Phone Number *", value=cust.get("phone", ""))
            email = st.text_input("Email Address", value=cust.get("email", ""))
            
        gst_number = st.text_input("GSTIN (Required for B2B)", value=cust.get("gst_number", ""))
        address = st.text_area("Full Address / Billing Address", value=cust.get("address_line1", ""))

        submitted = st.form_submit_button("Save Customer", type="primary", use_container_width=True)
        
        if submitted:
            errors = []
            
            ok, msg = validate_required(name, "Customer Name"); not ok and errors.append(msg)
            ok, msg = validate_phone(phone); not ok and errors.append(msg)
            
            if email:
                ok, msg = validate_email(email); not ok and errors.append(msg)
            if gst_number:
                ok, msg = validate_gst_number(gst_number); not ok and errors.append(msg)
            if ctype == "Select":
                errors.append("Please select a customer type.")
                
            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                data = {
                    "name": name,
                    "customer_type": ctype,
                    "email": email,
                    "phone": phone,
                    "gst_number": gst_number.upper() if gst_number else None,
                    "address_line1": address,
                }
                
                uid = get_current_user()["id"]
                if is_edit:
                    ok, msg = CustomerModel.update(customer_id, data, uid)
                else:
                    ok, msg = CustomerModel.create(data, uid)
                    
                if ok:
                    st.success("Saved successfully!")
                    st.session_state["_refresh_trigger"] = True
                    st.rerun()
                else:
                    st.error(f"Error: {msg}")

# ─── Main Render ──────────────────────────────────────────────────────────────

def render():
    require_auth()

    # Navbar
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">Customers</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    # ─── Toolbar ──────────────────────────────────────────────────────────────
    t_col1, t_col2, t_col3 = st.columns([2, 1, 1], gap="medium")
    with t_col1:
        search = st.text_input("🔍 Search Customers", placeholder="Search by name, phone, email, GST...", label_visibility="collapsed")
    with t_col2:
        filter_type = st.selectbox("Filter by Type", options=["All"] + CUSTOMER_TYPES, label_visibility="collapsed")
    with t_col3:
        if st.button("➕ Add Customer", use_container_width=True, type="primary"):
            _customer_form_dialog()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── Fetch Data ───────────────────────────────────────────────────────────
    customers = CustomerModel.get_all(search_query=search, customer_type=filter_type)
    
    if not customers:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">👥</div>
  <div class="empty-state-title">No customers found</div>
  <div class="empty-state-desc">Try adjusting your search or add a new customer.</div>
</div>
""", 
            unsafe_allow_html=True
        )
        return

    # ─── Render View ──────────────────────────────────────────────────────────
    rows_html = ""
    for c in customers:
        contact_html = ""
        if c['phone']:
            contact_html += f"<div><i class='fa-solid fa-phone' style='width:16px;'></i> {c['phone']}</div>"
        if c['email']:
            contact_html += f"<div><i class='fa-solid fa-envelope' style='width:16px;'></i> {c['email']}</div>"
            
        gst_html = f"<div style='font-family:monospace;margin-top:4px;'>GST: {c['gst_number']}</div>" if c['gst_number'] else ""
        
        # Color code customer types
        type_colors = {
            "retail": "#6C63FF",
            "contractor": "#FFB703",
            "wholesale": "#00D4AA"
        }
        type_color = type_colors.get(c['customer_type'], "#8B92A9")
        type_badge = f"<span style='background:{type_color}22;color:{type_color};border:1px solid {type_color}44;padding:2px 8px;border-radius:20px;font-size:0.7rem;font-weight:700;text-transform:uppercase;'>{c['customer_type']}</span>"
            
        rows_html += f"""<tr>
<td>
<div style="font-weight:600; font-size: 1rem; color: var(--text);margin-bottom:4px;">{c['name']}</div>
{type_badge}
</td>
<td style="font-size:0.85rem; color:var(--text-secondary); line-height:1.6;">
{contact_html}
</td>
<td style="font-size:0.85rem; color:var(--text-muted);">
{c.get('address_line1') or '-'}
{gst_html}
</td>
<td>
<span style="color:var(--text-muted);font-size:0.75rem;">See actions below</span>
</td>
</tr>"""
        
    st.markdown(
        f"""
<div class="paintpro-table-wrapper" style="margin-bottom: 20px;">
    <table class="paintpro-table">
        <thead>
            <tr>
                <th style="width:25%">Customer</th>
                <th style="width:25%">Contact Info</th>
                <th style="width:35%">Address & Tax Info</th>
                <th style="width:15%">Actions</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
""", 
        unsafe_allow_html=True
    )

    # Interactive Action Grid for Edit/Delete
    st.markdown("#### Quick Actions")
    cols_per_row = 4
    for i in range(0, len(customers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(customers):
                c = customers[i + j]
                with cols[j]:
                    st.markdown(f"**{c['name']}**")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✏️ Edit", key=f"edit_{c['id']}", use_container_width=True):
                            _customer_form_dialog(c['id'])
                    with ac2:
                        if st.button("🗑️ Del", key=f"del_{c['id']}", use_container_width=True):
                            _delete_dialog(c['id'], c['name'])
                    st.markdown("<br>", unsafe_allow_html=True)
                    
    st.markdown("</div>", unsafe_allow_html=True)
