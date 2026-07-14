"""
PaintPro Inventory Management System
=====================================
Stock Management Page  |  pages/stock_management.py

Manual stock adjustments, opening stock entries, and
complete audit trail of every inventory movement.
"""

import streamlit as st
from datetime import date
from utils.auth import require_auth, get_current_user
from utils.validators import validate_required
from utils.formatting import format_currency, format_date, format_stock
from database.connection import execute_query, execute_one, execute_write
from config.constants import STOCK_ADJUSTMENT_REASONS, STORAGE_LOCATIONS


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_products_dropdown():
    """Return [(id, sku – name, unit)] for the select widget."""
    rows = execute_query(
        "SELECT id, sku, name, unit, current_stock FROM products WHERE is_active=1 ORDER BY name"
    ) or []
    return rows


def _get_stock_logs(product_id=None, ref_type=None, limit=200):
    sql = """
        SELECT sl.id, sl.reference_type, sl.quantity_before, sl.quantity_change,
               sl.quantity_after, sl.unit_cost, sl.notes, sl.created_at,
               p.name AS product_name, p.sku, p.unit,
               u.full_name AS created_by_name
        FROM stock_logs sl
        JOIN products p ON sl.product_id = p.id
        LEFT JOIN users u ON sl.user_id = u.id
        WHERE 1=1
    """
    params = []
    if product_id:
        sql += " AND sl.product_id = %s"
        params.append(product_id)
    if ref_type and ref_type != "All":
        sql += " AND sl.reference_type = %s"
        params.append(ref_type.lower())
    sql += " ORDER BY sl.created_at DESC LIMIT %s"
    params.append(limit)
    return execute_query(sql, tuple(params)) or []


def _apply_adjustment(product_id, change_qty, reason, notes, unit_cost, user_id):
    """Apply a manual stock adjustment atomically."""
    product = execute_one(
        "SELECT current_stock FROM products WHERE id=%s", (product_id,)
    )
    if not product:
        return False, "Product not found."

    qty_before = float(product["current_stock"])
    qty_after  = qty_before + change_qty

    if qty_after < 0:
        return False, f"Adjustment would result in negative stock ({qty_after:.2f}). Not allowed."

    try:
        execute_write(
            "UPDATE products SET current_stock=%s WHERE id=%s",
            (qty_after, product_id),
        )
        execute_write(
            """
            INSERT INTO stock_logs
              (product_id, user_id, reference_type, quantity_before,
               quantity_change, quantity_after, unit_cost, notes)
            VALUES (%s,%s,'adjustment',%s,%s,%s,%s,%s)
            """,
            (product_id, user_id, qty_before, change_qty, qty_after,
             unit_cost or None, f"{reason}: {notes}" if notes else reason),
        )
        return True, f"Stock updated: {qty_before:.2f} → {qty_after:.2f}"
    except Exception as exc:
        return False, str(exc)


# ─── Main Render ─────────────────────────────────────────────────────────────

def render():
    require_auth()

    st.markdown("## 🏭 Stock Management")
    st.caption("Perform manual adjustments, open opening stock entries, and audit every inventory movement.")
    st.divider()

    tab_adjust, tab_log = st.tabs(["📝 Manual Adjustment", "📋 Stock Movement Log"])

    # ── TAB 1: Adjustment ─────────────────────────────────────────────────────
    with tab_adjust:
        products = _get_products_dropdown()
        if not products:
            st.warning("No active products found. Add products in the Inventory page first.")
            return

        prod_map = {p["id"]: f"{p['sku']} - {p['name']}" for p in products}
        prod_ids = list(prod_map.keys())
        prod_labels = list(prod_map.values())

        st.markdown("### Adjust Stock Level")
        col_form, col_info = st.columns([3, 2], gap="large")

        with col_form:
            with st.form("stock_adjust_form"):
                selected_label = st.selectbox(
                    "Select Product *",
                    options=prod_labels,
                )
                selected_idx  = prod_labels.index(selected_label)
                selected_pid  = prod_ids[selected_idx]

                adj_type = st.radio(
                    "Adjustment Type",
                    ["Add Stock (+)", "Remove Stock (−)", "Set Exact Quantity"],
                    horizontal=True,
                )
                qty_input = st.number_input(
                    "Quantity *",
                    min_value=0.0, step=1.0, format="%.2f",
                )
                reason = st.selectbox("Reason *", STOCK_ADJUSTMENT_REASONS)
                notes  = st.text_area("Notes / Reference", height=80)
                unit_cost = st.number_input(
                    "Unit Cost (optional, for valuation)",
                    min_value=0.0, step=0.01, format="%.2f",
                )

                submitted = st.form_submit_button(
                    "Apply Adjustment", type="primary", use_container_width=True
                )

                if submitted:
                    uid = get_current_user()["id"]
                    prod = next((p for p in products if p["id"] == selected_pid), None)

                    if qty_input == 0 and adj_type != "Set Exact Quantity":
                        st.error("❌ Quantity must be greater than 0.")
                    else:
                        if adj_type == "Add Stock (+)":
                            change = qty_input
                        elif adj_type == "Remove Stock (−)":
                            change = -qty_input
                        else:  # Set Exact
                            current = float(prod["current_stock"])
                            change  = qty_input - current

                        ok, msg = _apply_adjustment(
                            selected_pid, change, reason, notes, unit_cost, uid
                        )
                        if ok:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

        with col_info:
            st.markdown("#### Current Stock Levels")
            # Show low-stock products
            low = [p for p in products if float(p["current_stock"]) == 0]
            if low:
                st.error(f"🚨 {len(low)} product(s) are out of stock")

            for p in products[:12]:
                stock_val = float(p["current_stock"])
                color = "#00D4AA" if stock_val > 5 else ("#FFB703" if stock_val > 0 else "#FF4757")
                st.markdown(
                    f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:6px 0;border-bottom:1px solid #2D3250;">
  <span style="font-size:0.8rem;color:#B8BDD9;overflow:hidden;
               text-overflow:ellipsis;white-space:nowrap;max-width:180px;">
    {p['sku']} - {p['name']}
  </span>
  <span style="font-size:0.8rem;font-weight:700;color:{color};flex-shrink:0;">
    {stock_val:.0f} {p['unit']}
  </span>
</div>
""",
                    unsafe_allow_html=True,
                )

    # ── TAB 2: Movement Log ───────────────────────────────────────────────────
    with tab_log:
        st.markdown("### Stock Movement History")

        f1, f2, f3 = st.columns([3, 2, 1])
        with f1:
            search_prod = st.text_input("🔍 Filter by product", label_visibility="collapsed",
                                         placeholder="Product SKU or name…")
        with f2:
            type_filter = st.selectbox(
                "Type",
                ["All", "purchase", "sale", "adjustment", "return_in", "return_out",
                 "damaged", "opening", "transfer"],
                label_visibility="collapsed",
            )
        with f3:
            st.markdown("&nbsp;")

        # Resolve product filter to ID
        pid_filter = None
        if search_prod:
            match = execute_one(
                "SELECT id FROM products WHERE (sku LIKE %s OR name LIKE %s) AND is_active=1 LIMIT 1",
                (f"%{search_prod}%", f"%{search_prod}%"),
            )
            pid_filter = match["id"] if match else -1  # -1 = no match found

        logs = _get_stock_logs(product_id=pid_filter, ref_type=type_filter)

        if not logs:
            st.info("No stock movements found for the selected filters.")
        else:
            st.caption(f"Showing {len(logs)} records")

            type_colors = {
                "purchase": "#00D4AA", "sale": "#FF6B6B",
                "adjustment": "#6C63FF", "return_in": "#2BCBBA",
                "return_out": "#FFB703", "damaged": "#FF4757",
                "opening": "#8B85FF", "transfer": "#B8BDD9",
            }

            rows_html = ""
            for log in logs:
                change = float(log["quantity_change"])
                sign  = "+" if change >= 0 else ""
                chg_color = "#00D4AA" if change >= 0 else "#FF4757"
                tc = type_colors.get(log["reference_type"], "#8B92A9")
                rows_html += f"""
<tr>
  <td style="font-size:0.78rem;color:#8B92A9;">{format_date(log['created_at'])}</td>
  <td>
    <div style="font-weight:600;font-size:0.85rem;">{log['product_name']}</div>
    <div style="font-size:0.72rem;color:#8B92A9;">{log['sku']}</div>
  </td>
  <td>
    <span style="background:{tc}22;color:{tc};border:1px solid {tc}44;
                 padding:2px 8px;border-radius:20px;font-size:0.72rem;font-weight:700;">
      {log['reference_type'].replace('_',' ').title()}
    </span>
  </td>
  <td style="text-align:right;font-size:0.85rem;">{float(log['quantity_before']):.2f}</td>
  <td style="text-align:right;font-weight:700;color:{chg_color};font-size:0.9rem;">
    {sign}{change:.2f}
  </td>
  <td style="text-align:right;font-size:0.85rem;">{float(log['quantity_after']):.2f}</td>
  <td style="font-size:0.78rem;color:#8B92A9;">{log.get('created_by_name') or '-'}</td>
  <td style="font-size:0.75rem;color:#8B92A9;max-width:150px;overflow:hidden;
             text-overflow:ellipsis;white-space:nowrap;">
    {log.get('notes') or '-'}
  </td>
</tr>
"""

            st.markdown(
                f"""
<div class="paintpro-table-wrapper">
  <table class="paintpro-table">
    <thead>
      <tr>
        <th>Date</th>
        <th>Product</th>
        <th>Type</th>
        <th style="text-align:right">Before</th>
        <th style="text-align:right">Change</th>
        <th style="text-align:right">After</th>
        <th>By</th>
        <th>Notes</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""",
                unsafe_allow_html=True,
            )
