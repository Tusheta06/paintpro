"""
PaintPro Inventory Management System
=====================================
Brands Page  |  pages/brands.py

Manage product brands/manufacturers: view, add, edit, delete.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.validators import validate_required
from models.brand import BrandModel

# ─── Modal Dialogs ────────────────────────────────────────────────────────────

@st.dialog("Delete Brand")
def _delete_dialog(brand_id: int, brand_name: str):
    st.warning(f"Are you sure you want to delete the brand **{brand_name}**?")
    st.markdown("Brands linked to active products cannot be deleted.")
    
    col1, col2 = st.columns(2)
    if col1.button("Cancel", use_container_width=True):
        st.rerun()
    if col2.button("Yes, Delete", type="primary", use_container_width=True):
        ok, msg = BrandModel.delete(brand_id, get_current_user()["id"])
        if ok:
            st.success("Brand deleted successfully!")
            st.session_state["_refresh_trigger"] = True
            st.rerun()
        else:
            st.error(f"Failed to delete: {msg}")

@st.dialog("Brand Form", width="small")
def _brand_form_dialog(brand_id: int = None):
    is_edit = brand_id is not None
    brand = {}
    if is_edit:
        brand = BrandModel.get_by_id(brand_id)
        if not brand:
            st.error("Brand not found.")
            return

    st.markdown(f"### {'Edit' if is_edit else 'Add'} Brand")
    
    with st.form("brand_form"):
        name = st.text_input("Brand Name *", value=brand.get("name", ""))
        # mfg = st.text_input("Manufacturer/Parent Company", value=brand.get("manufacturer", ""))
        desc = st.text_area("Description", value=brand.get("description", ""))

        submitted = st.form_submit_button("Save Brand", type="primary", use_container_width=True)
        
        if submitted:
            ok, msg = validate_required(name, "Name")
            if not ok:
                st.error(f"❌ {msg}")
            else:
                data = {
                    "name": name,
                    # "manufacturer": mfg,
                    "description": desc,
                }
                
                uid = get_current_user()["id"]
                if is_edit:
                    ok, msg = BrandModel.update(brand_id, data, uid)
                else:
                    ok, msg = BrandModel.create(data, uid)
                    
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
    <div class="navbar-page-title">Brands</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    # ─── Toolbar ──────────────────────────────────────────────────────────────
    t_col1, t_col2, t_col3 = st.columns([2, 1, 1], gap="medium")
    with t_col1:
        search = st.text_input("🔍 Search Brands", placeholder="Search by name or description...", label_visibility="collapsed")
    with t_col2:
        pass # Spacer
    with t_col3:
        if st.button("➕ Add Brand", use_container_width=True, type="primary"):
            _brand_form_dialog()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── Fetch Data ───────────────────────────────────────────────────────────
    brands = BrandModel.get_all(search_query=search)
    
    if not brands:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">🏷️</div>
  <div class="empty-state-title">No brands found</div>
  <div class="empty-state-desc">Try adjusting your search or add a new brand.</div>
</div>
""", 
            unsafe_allow_html=True
        )
        return

    # ─── Render View ──────────────────────────────────────────────────────────
    rows_html = ""

    for b in brands:
        rows_html += f"""<tr>
<td>
<div style="font-weight:600; font-size:0.95rem;">{b['name']}</div>
</td>
<td style="color:var(--text-muted);">
{b.get('description') or '-'}
</td>
</tr>"""
        
    st.markdown(
        f"""
<div class="paintpro-table-wrapper" style="margin-bottom: 20px;">
    <table class="paintpro-table">
        <thead>
            <tr>
                <th style="width:30%">Brand Name</th>
                <th style="width:70%">Description</th>
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
    for i in range(0, len(brands), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(brands):
                b = brands[i + j]
                with cols[j]:
                    st.markdown(f"**{b['name']}**")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✏️ Edit", key=f"edit_{b['id']}", use_container_width=True):
                            _brand_form_dialog(b['id'])
                    with ac2:
                        if st.button("🗑️ Del", key=f"del_{b['id']}", use_container_width=True):
                            _delete_dialog(b['id'], b['name'])
                    st.markdown("<br>", unsafe_allow_html=True)
                    
    st.markdown("</div>", unsafe_allow_html=True)
