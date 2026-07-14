"""
PaintPro Inventory Management System
=====================================
Categories Page  |  pages/categories.py

Manage product categories: view, add, edit, delete.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.validators import validate_required
from models.category import CategoryModel

# ─── Modal Dialogs ────────────────────────────────────────────────────────────

@st.dialog("Delete Category")
def _delete_dialog(category_id: int, category_name: str):
    st.warning(f"Are you sure you want to delete the category **{category_name}**?")
    st.markdown("Categories linked to active products cannot be deleted.")
    
    col1, col2 = st.columns(2)
    if col1.button("Cancel", use_container_width=True):
        st.rerun()
    if col2.button("Yes, Delete", type="primary", use_container_width=True):
        ok, msg = CategoryModel.delete(category_id, get_current_user()["id"])
        if ok:
            st.success("Category deleted successfully!")
            st.session_state["_refresh_trigger"] = True
            st.rerun()
        else:
            st.error(f"Failed to delete: {msg}")

@st.dialog("Category Form", width="small")
def _category_form_dialog(category_id: int = None):
    is_edit = category_id is not None
    cat = {}
    if is_edit:
        cat = CategoryModel.get_by_id(category_id)
        if not cat:
            st.error("Category not found.")
            return

    st.markdown(f"### {'Edit' if is_edit else 'Add'} Category")
    
    with st.form("category_form"):
        name = st.text_input("Category Name *", value=cat.get("name", ""))
        desc = st.text_area("Description", value=cat.get("description", ""))

        submitted = st.form_submit_button("Save Category", type="primary", use_container_width=True)
        
        if submitted:
            ok, msg = validate_required(name, "Name")
            if not ok:
                st.error(f"❌ {msg}")
            else:
                data = {
                    "name": name,
                    "description": desc,
                }
                
                uid = get_current_user()["id"]
                if is_edit:
                    ok, msg = CategoryModel.update(category_id, data, uid)
                else:
                    ok, msg = CategoryModel.create(data, uid)
                    
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
    <div class="navbar-page-title">Categories</div>
</div>
""",
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='padding: 24px;'>", unsafe_allow_html=True)
    
    # ─── Toolbar ──────────────────────────────────────────────────────────────
    t_col1, t_col2, t_col3 = st.columns([2, 1, 1], gap="medium")
    with t_col1:
        search = st.text_input("🔍 Search Categories", placeholder="Search by name...", label_visibility="collapsed")
    with t_col2:
        pass # Spacer
    with t_col3:
        if st.button("➕ Add Category", use_container_width=True, type="primary"):
            _category_form_dialog()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── Fetch Data ───────────────────────────────────────────────────────────
    categories = CategoryModel.get_all(search_query=search)
    
    if not categories:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">📁</div>
  <div class="empty-state-title">No categories found</div>
  <div class="empty-state-desc">Try adjusting your search or add a new category.</div>
</div>
""", 
            unsafe_allow_html=True
        )
        return

    # ─── Render View ──────────────────────────────────────────────────────────
    rows_html = ""
    for c in categories:
        rows_html += f"""
<tr>
    <td style="font-weight:600; font-size: 0.95rem;">{c['name']}</td>
    <td style="color:var(--text-muted);">{c['description'] or '-'}</td>
</tr>
"""
        
    st.markdown(
        f"""
<div class="paintpro-table-wrapper" style="margin-bottom: 20px;">
    <table class="paintpro-table">
        <thead>
            <tr>
                <th style="width:30%">Name</th>
                <th style="width:70%">Description</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
""", 
        unsafe_allow_html=True
    )

    # Interactive Action Grid for Edit/Delete since we can't easily put streamlit buttons in HTML table
    st.markdown("#### Quick Actions")
    cols_per_row = 4
    for i in range(0, len(categories), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(categories):
                c = categories[i + j]
                with cols[j]:
                    st.markdown(f"**{c['name']}**")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✏️ Edit", key=f"edit_{c['id']}", use_container_width=True):
                            _category_form_dialog(c['id'])
                    with ac2:
                        if st.button("🗑️ Del", key=f"del_{c['id']}", use_container_width=True):
                            _delete_dialog(c['id'], c['name'])
                    st.markdown("<br>", unsafe_allow_html=True)
                    
    st.markdown("</div>", unsafe_allow_html=True)
