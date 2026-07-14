"""
PaintPro Inventory Management System
=====================================
Color Preview Component  |  components/color_preview.py

Renders a beautiful paint color swatch card displaying HEX, RGB,
and paint finish metadata.
"""

import streamlit as st

def render_color_swatch(hex_color: str, rgb_color: str, color_name: str, finish: str = ""):
    """Render a standalone color swatch."""
    if not hex_color:
        hex_color = "#FFFFFF"
    
    html = f"""
<div style="
    width: 100%;
    height: 80px;
    background-color: {hex_color};
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 8px;
">
    <div style="
        background: rgba(0,0,0,0.5);
        backdrop-filter: blur(4px);
        color: #fff;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        align-self: flex-start;
        font-family: monospace;
    ">
        {hex_color}
    </div>
</div>
<div style="margin-top: 8px;">
    <div style="font-weight: 600; font-size: 0.9rem; color: var(--text);">{color_name or 'N/A'}</div>
    <div style="font-size: 0.75rem; color: var(--text-muted);">
        RGB: {rgb_color or 'N/A'} {f'• {finish}' if finish else ''}
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def render_product_color_card(product: dict):
    """Render a complete product card with its color swatch (Premium Feature 2)."""
    hex_color = product.get("color_hex") or "#F4F6FB"
    color_name = product.get("color_name") or "Standard"
    price = product.get("selling_price", 0)
    stock = product.get("current_stock", 0)
    
    html = f"""
<div class="color-card">
    <div class="color-swatch" style="background-color: {hex_color};">
        <div class="color-hex-pill">{hex_color}</div>
    </div>
    <div class="color-card-body">
        <div class="color-product-name" title="{product.get('name', '')}">{product.get('name', 'Unknown Product')}</div>
        <div class="color-product-meta">
            {product.get('brand_name', '')} • {product.get('pack_size', '')}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
            <div class="color-product-price">₹{float(price):,.2f}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">
                Stock: <b>{float(stock):g}</b>
            </div>
        </div>
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
