"""
PaintPro Inventory Management System
=====================================
Suppliers Page  |  pages/suppliers.py

Manage supplier and vendor relationships: view, add, edit, delete.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.validators import validate_required, validate_email, validate_phone, validate_gst_number
from models.supplier import SupplierModel

# ─── Modal Dialogs ────────────────────────────────────────────────────────────

@st.dialog("Delete Supplier")
def _delete_dialog(supplier_id: int, supplier_name: str):
    st.warning(f"Are you sure you want to delete the supplier **{supplier_name}**?")
    st.markdown("Suppliers with existing purchase records cannot be deleted to preserve financial history.")
    
    col1, col2 = st.columns(2)
    if col1.button("Cancel", use_container_width=True):
        st.rerun()
    if col2.button("Yes, Delete", type="primary", use_container_width=True):
        ok, msg = SupplierModel.delete(supplier_id, get_current_user()["id"])
        if ok:
            st.success("Supplier deleted successfully!")
            st.session_state["_refresh_trigger"] = True
            st.rerun()
        else:
            st.error(f"Failed to delete: {msg}")

@st.dialog("Supplier Form", width="large")
def _supplier_form_dialog(supplier_id: int = None):
    is_edit = supplier_id is not None
    sup = {}
    if is_edit:
        sup = SupplierModel.get_by_id(supplier_id)
        if not sup:
            st.error("Supplier not found.")
            return

    st.markdown(f"### {'Edit' if is_edit else 'Add'} Supplier")
    
    with st.form("supplier_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Company/Supplier Name *", value=sup.get("name", ""))
            contact_person = st.text_input("Contact Person", value=sup.get("contact_person", ""))
        with col2:
            gst_number = st.text_input("GSTIN", value=sup.get("gst_number", ""))
            st.caption("15-character GST format")
            
        c1, c2 = st.columns(2)
        with c1:
            phone = st.text_input("Phone Number *", value=sup.get("phone", ""))
        with c2:
            email = st.text_input("Email Address", value=sup.get("email", ""))
            
        address = st.text_area("Full Address", value=sup.get("address_line1", ""))

        submitted = st.form_submit_button("Save Supplier", type="primary", use_container_width=True)
        
        if submitted:
            errors = []
            
            ok, msg = validate_required(name, "Company Name"); not ok and errors.append(msg)
            ok, msg = validate_phone(phone); not ok and errors.append(msg)
            
            if email:
                ok, msg = validate_email(email); not ok and errors.append(msg)
            if gst_number:
                ok, msg = validate_gst_number(gst_number); not ok and errors.append(msg)
                
            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                data = {
                    "name": name,
                    "contact_person": contact_person,
                    "email": email,
                    "phone": phone,
                    "gst_number": gst_number.upper() if gst_number else None,
                    "address_line1": address,
                }
                
                uid = get_current_user()["id"]
                if is_edit:
                    ok, msg = SupplierModel.update(supplier_id, data, uid)
                else:
                    ok, msg = SupplierModel.create(data, uid)
                    
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
    <div class="navbar-page-title">Suppliers & Vendors</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    # ─── Toolbar ──────────────────────────────────────────────────────────────
    t_col1, t_col2, t_col3 = st.columns([2, 1, 1], gap="medium")
    with t_col1:
        search = st.text_input("🔍 Search Suppliers", placeholder="Search by name, contact, phone, GST...", label_visibility="collapsed")
    with t_col2:
        pass # Spacer
    with t_col3:
        if st.button("➕ Add Supplier", use_container_width=True, type="primary"):
            _supplier_form_dialog()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── Fetch Data ───────────────────────────────────────────────────────────
    suppliers = SupplierModel.get_all(search_query=search)
    
    if not suppliers:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">🏢</div>
  <div class="empty-state-title">No suppliers found</div>
  <div class="empty-state-desc">Try adjusting your search or add a new supplier.</div>
</div>
""", 
            unsafe_allow_html=True
        )
        return

    # ─── Render View ──────────────────────────────────────────────────────────
    rows_html = ""
    for s in suppliers:
        contact_html = ""
        if s['contact_person']:
            contact_html += f"<div><i class='fa-solid fa-user' style='width:16px;'></i> {s['contact_person']}</div>"
        if s['phone']:
            contact_html += f"<div><i class='fa-solid fa-phone' style='width:16px;'></i> {s['phone']}</div>"
        if s['email']:
            contact_html += f"<div><i class='fa-solid fa-envelope' style='width:16px;'></i> {s['email']}</div>"
            
        gst_html = f"<div style='font-family:monospace;margin-top:4px;'>GST: {s['gst_number']}</div>" if s['gst_number'] else ""
            
        rows_html += f"""<tr>
<td>
<div style="font-weight:600; font-size: 1rem; color: var(--primary-light);">{s['name']}</div>
{gst_html}
</td>
<td style="font-size:0.85rem; color:var(--text-secondary); line-height:1.6;">
{contact_html}
</td>
<td style="font-size:0.85rem; color:var(--text-muted);">
{s.get('address_line1') or '-'}
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
                <th style="width:25%">Company</th>
                <th style="width:25%">Contact Info</th>
                <th style="width:35%">Address</th>
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
    for i in range(0, len(suppliers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(suppliers):
                s = suppliers[i + j]
                with cols[j]:
                    st.markdown(f"**{s['name']}**")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✏️ Edit", key=f"edit_{s['id']}", use_container_width=True):
                            _supplier_form_dialog(s['id'])
                    with ac2:
                        if st.button("🗑️ Del", key=f"del_{s['id']}", use_container_width=True):
                            _delete_dialog(s['id'], s['name'])
                    st.markdown("<br>", unsafe_allow_html=True)
                    
    st.markdown("</div>", unsafe_allow_html=True)
