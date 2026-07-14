"""
PaintPro Inventory Management System
=====================================
Plotly Charts Component  |  components/charts.py

Wrappers for generating consistent, theme-aware Plotly charts.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.settings import theme_config

# Common chart layout settings for dark theme
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#B4BAD8", family="Inter, sans-serif"),
    margin=dict(l=10, r=10, t=40, b=20),
    hovermode="x unified",
    colorway=["#6C63FF", "#00D4AA", "#FFB703", "#FF6B6B", "#38BDF8"],
    hoverlabel=dict(
        bgcolor="#1E2235",
        bordercolor="#2A2F4A",
        font=dict(color="#F0F2FF", size=12),
    ),
    xaxis=dict(
        gridcolor="#2A2F4A",
        tickcolor="#2A2F4A",
        linecolor="#2A2F4A",
        tickfont=dict(color="#7B82A3"),
    ),
    yaxis=dict(
        gridcolor="#2A2F4A",
        tickcolor="#2A2F4A",
        linecolor="#2A2F4A",
        tickfont=dict(color="#7B82A3"),
    )
)

def render_revenue_trend(df: pd.DataFrame, x_col: str, y_col: str, title: str = "Revenue Trend"):
    """Render a smooth line chart for revenue over time."""
    if df.empty:
        return _empty_chart("No revenue data available")

    fig = px.area(
        df, 
        x=x_col, 
        y=y_col, 
        title=title,
        color_discrete_sequence=[theme_config.PRIMARY_COLOR]
    )
    
    fig.update_layout(CHART_LAYOUT)
    fig.update_traces(
        line=dict(width=3, color=theme_config.PRIMARY_COLOR),
        fillcolor=f"rgba(108, 99, 255, 0.2)"
    )
    fig.update_xaxes(showgrid=False, title_text="")
    fig.update_yaxes(showgrid=True, title_text="")
    
    return fig

def render_sales_by_category(df: pd.DataFrame, names_col: str, values_col: str, title: str = "Sales by Category"):
    """Render a donut chart for categorical breakdown."""
    if df.empty:
        return _empty_chart("No sales data available")

    fig = px.pie(
        df, 
        names=names_col, 
        values=values_col, 
        hole=0.6,
        title=title,
        color_discrete_sequence=[
            theme_config.PRIMARY_COLOR, 
            theme_config.SUCCESS_COLOR, 
            theme_config.WARNING_COLOR,
            theme_config.SECONDARY_COLOR,
            theme_config.INFO_COLOR
        ]
    )
    
    fig.update_layout(CHART_LAYOUT)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig.update_traces(textposition='inside', textinfo='percent')
    
    return fig

def render_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "Chart", color: str = None):
    """Render a vertical bar chart (e.g. for top selling products)."""
    if df.empty:
        return _empty_chart("No data available")

    color_val = color if color else theme_config.PRIMARY_COLOR
    fig = px.bar(
        df, 
        x=x_col, 
        y=y_col, 
        title=title,
        color_discrete_sequence=[color_val]
    )
    
    fig.update_layout(CHART_LAYOUT)
    fig.update_traces(marker_border_width=0, opacity=0.9)
    fig.update_xaxes(showgrid=False, title_text="")
    fig.update_yaxes(showgrid=True, title_text="")
    
    return fig

def _empty_chart(message: str):
    """Return a blank chart with a centered text message for empty states."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color=theme_config.DARK_MUTED_TEXT)
    )
    fig.update_layout(CHART_LAYOUT)
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)
    return fig
