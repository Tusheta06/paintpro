"""
PaintPro Inventory Management System
=====================================
Analytics & AI Alerts Page  |  pages/analytics.py

Displays predictive stockout alerts, advanced business analytics,
and bar chart visualizations for data insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.auth import require_auth
from utils.formatting import format_currency
from utils.ai_predict import get_predictive_stock_alerts
from components.charts import CHART_LAYOUT, _empty_chart



_STATUS_COLORS = {
    'Safe':                   '#00D4AA',
    'Warning (< 1 month)':    '#FFB703',
    'Critical (< 2 weeks)':   '#FF4757',
    'Below Minimum':          '#9B93FF',
    'Stockout':               '#7B82A3',
}

# ─── Render ───────────────────────────────────────────────────────────────────

def render():
    require_auth()

    # Navbar
    st.markdown(
        """
<div class="paintpro-navbar">
    <div class="navbar-page-title">📈 AI Analytics &amp; Predictions</div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div style="margin-bottom:6px;">
  <span style="font-size:1.35rem;font-weight:800;letter-spacing:-0.5px;color:var(--text);">
    AI Predictive Stock Intelligence
  </span><br>
  <span style="color:var(--text-muted);font-size:0.875rem;line-height:1.6;">
    Sales velocity analysed over the past 30 days to predict stockouts,
    suggest reorder quantities, and surface critical restocking opportunities.
  </span>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    with st.spinner("Analysing sales velocity…"):
        df_alerts = get_predictive_stock_alerts(days_window=30)

    if df_alerts.empty:
        st.info("No active products found to analyse.")
        return

    df_critical = df_alerts[df_alerts['ai_status'] != 'Safe']

    # ─── KPI Cards ────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(f"""
<div class="kpi-card" style="border-color:var(--danger);">
  <div class="kpi-card-header">
    <div class="kpi-card-label">Stockouts</div>
    <div class="kpi-card-icon" style="background:rgba(255,71,87,0.12);color:#FF4757;font-size:1.2rem;">🚨</div>
  </div>
  <div class="kpi-card-value" style="color:#FF4757;">{len(df_alerts[df_alerts['ai_status'] == 'Stockout'])}</div>
  <div class="kpi-card-sub">Items completely out</div>
</div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
<div class="kpi-card" style="border-color:var(--warning);">
  <div class="kpi-card-header">
    <div class="kpi-card-label">Critical (&lt;14 days)</div>
    <div class="kpi-card-icon" style="background:rgba(255,183,3,0.12);color:#FFB703;font-size:1.2rem;">⚠️</div>
  </div>
  <div class="kpi-card-value" style="color:#FFB703;">{len(df_alerts[df_alerts['ai_status'] == 'Critical (< 2 weeks)'])}</div>
  <div class="kpi-card-sub">Will empty in &lt; 2 weeks</div>
</div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-card-header">
    <div class="kpi-card-label">To Reorder</div>
    <div class="kpi-card-icon" style="font-size:1.2rem;">📦</div>
  </div>
  <div class="kpi-card-value">{len(df_critical)}</div>
  <div class="kpi-card-sub">Total items needing action</div>
</div>""", unsafe_allow_html=True)

    with c4:
        total_investment = df_critical['estimated_cost'].sum()
        st.markdown(f"""
<div class="kpi-card" style="border-color:var(--primary);background:linear-gradient(135deg,rgba(108,99,255,0.08),rgba(108,99,255,0.02));">
  <div class="kpi-card-header">
    <div class="kpi-card-label">Est. Reorder Cost</div>
    <div class="kpi-card-icon" style="background:rgba(108,99,255,0.15);color:var(--primary-light);font-size:1.2rem;">💰</div>
  </div>
  <div class="kpi-card-value" style="color:var(--primary-light);font-size:1.5rem;">{format_currency(total_investment)}</div>
  <div class="kpi-card-sub">To replenish all critical items</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ─── Tabs: Table | Bar Charts | Scatter ───────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋  Restock List", "📊  Bar Chart Analysis", "🔵  Scatter Matrix"])

    # ── Tab 1: Restock List ───────────────────────────────────────────────────
    with tab1:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if df_critical.empty:
            st.success("🎉 Your inventory is perfectly balanced! No critical restocks required.")
        else:
            df_display = df_critical.copy()
            df_display['daily_velocity'] = df_display['daily_velocity'].apply(lambda x: f"{x:.2f}/day")
            df_display['days_remaining'] = df_display['days_remaining'].apply(
                lambda x: f"{int(x)} days" if x != float('inf') else "—"
            )
            df_display['estimated_cost'] = df_display['estimated_cost'].apply(lambda x: format_currency(x))
            df_display = df_display[['sku', 'name', 'current_stock', 'daily_velocity',
                                     'days_remaining', 'ai_status', 'suggested_order_qty', 'estimated_cost']]
            df_display.columns = ['SKU', 'Product', 'Stock', 'Sales Velocity',
                                   'Est. Time to Empty', 'AI Status', 'Suggested PO Qty', 'Est. Cost']
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Tab 2: Bar Chart Analysis ─────────────────────────────────────────────
    with tab2:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2, gap="large")

        # ── Chart 1: Current Stock by Product (horizontal bar) ────────────────
        with col_a:
            st.markdown(
                "<div style='font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:12px;'>"
                "📦 Current Stock Levels by Product</div>",
                unsafe_allow_html=True,
            )
            df_stock = df_alerts.nlargest(12, 'current_stock').sort_values('current_stock')
            if not df_stock.empty:
                bar_colors = [_STATUS_COLORS.get(s, '#6C63FF') for s in df_stock['ai_status']]
                fig_stock = go.Figure(go.Bar(
                    x=df_stock['current_stock'],
                    y=df_stock['name'].apply(lambda n: n[:22] + '…' if len(n) > 22 else n),
                    orientation='h',
                    marker=dict(
                        color=bar_colors,
                        line=dict(color='rgba(0,0,0,0)', width=0),
                    ),
                    text=df_stock['current_stock'],
                    textposition='outside',
                    textfont=dict(color='#B4BAD8', size=11),
                    hovertemplate="<b>%{y}</b><br>Stock: %{x} units<extra></extra>",
                ))
                fig_stock.update_layout(CHART_LAYOUT)
                fig_stock.update_layout(
                    title=dict(text="", x=0),
                    height=420,
                    showlegend=False,
                    bargap=0.25,
                )
                fig_stock.update_xaxes(title_text="Units On Hand")
                fig_stock.update_yaxes(title_text="")
                st.plotly_chart(fig_stock, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No stock data available.")

        # ── Chart 2: Stock Status Distribution (grouped bar) ──────────────────
        with col_b:
            st.markdown(
                "<div style='font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:12px;'>"
                "🚦 Inventory Health by Status</div>",
                unsafe_allow_html=True,
            )
            status_counts = df_alerts['ai_status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            if not status_counts.empty:
                colors_mapped = [_STATUS_COLORS.get(s, '#6C63FF') for s in status_counts['Status']]
                fig_status = go.Figure(go.Bar(
                    x=status_counts['Status'],
                    y=status_counts['Count'],
                    marker=dict(
                        color=colors_mapped,
                        line=dict(color='rgba(0,0,0,0)', width=0),
                    ),
                    text=status_counts['Count'],
                    textposition='outside',
                    textfont=dict(color='#B4BAD8', size=11),
                    hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
                ))
                fig_status.update_layout(CHART_LAYOUT)
                fig_status.update_layout(
                    title=dict(text="", x=0),
                    height=420,
                    showlegend=False,
                    bargap=0.35,
                )
                fig_status.update_xaxes(title_text="Status")
                fig_status.update_yaxes(title_text="Number of Products")
                st.plotly_chart(fig_status, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No status data available.")

        # ── Chart 3: Daily Velocity vs Suggested Order (full-width bar) ───────
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:12px;'>"
            "🔄 Suggested Reorder Quantities vs. Current Stock</div>",
            unsafe_allow_html=True,
        )
        df_reorder = df_critical.nlargest(15, 'suggested_order_qty') if not df_critical.empty else pd.DataFrame()
        if not df_reorder.empty:
            short_names = df_reorder['name'].apply(lambda n: n[:20] + '…' if len(n) > 20 else n)
            fig_reorder = go.Figure()
            fig_reorder.add_trace(go.Bar(
                name='Current Stock',
                x=short_names,
                y=df_reorder['current_stock'],
                marker_color='rgba(108,99,255,0.65)',
                marker_line=dict(color='rgba(0,0,0,0)', width=0),
                hovertemplate="<b>%{x}</b><br>Current Stock: %{y}<extra></extra>",
            ))
            fig_reorder.add_trace(go.Bar(
                name='Suggested Order',
                x=short_names,
                y=df_reorder['suggested_order_qty'],
                marker_color='rgba(0,212,170,0.75)',
                marker_line=dict(color='rgba(0,0,0,0)', width=0),
                hovertemplate="<b>%{x}</b><br>Suggested Order: %{y}<extra></extra>",
            ))
            fig_reorder.update_layout(CHART_LAYOUT)
            fig_reorder.update_layout(
                title=dict(text="", x=0),
                height=380,
                barmode='group',
                bargap=0.22,
                bargroupgap=0.06,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    bgcolor='rgba(30,34,53,0.8)',
                    bordercolor='#2A2F4A',
                    borderwidth=1,
                    font=dict(color='#B4BAD8', size=11),
                ),
            )
            fig_reorder.update_xaxes(title_text="Product")
            fig_reorder.update_yaxes(title_text="Units")
            st.plotly_chart(fig_reorder, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No items require reordering right now. 🎉")

    # ── Tab 3: Scatter Matrix ─────────────────────────────────────────────────
    with tab3:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        df_plot = df_alerts[df_alerts['daily_velocity'] > 0]
        if not df_plot.empty:
            fig_scatter = px.scatter(
                df_plot,
                x='daily_velocity',
                y='current_stock',
                color='ai_status',
                hover_name='name',
                hover_data=['days_remaining'],
                title="Stock Balance Matrix — Lower Right is Critical",
                color_discrete_map=_STATUS_COLORS,
                size_max=18,
            )
            fig_scatter.update_traces(
                marker=dict(size=12, opacity=0.85, line=dict(width=1.5, color='rgba(255,255,255,0.15)'))
            )
            fig_scatter.update_layout(CHART_LAYOUT)
            fig_scatter.update_layout(
                height=480,
            )
            fig_scatter.update_xaxes(title_text="Daily Sales Velocity (Units sold/day)")
            fig_scatter.update_yaxes(title_text="Current Stock On Hand")
            st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Not enough sales data yet to generate the scatter matrix.")
