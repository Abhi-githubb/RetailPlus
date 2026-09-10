"""
Interactive Plotly Chart Builders for RetailPulse Dashboard.
Standardized typography, dark-slate background, brand colors, and interactive tooltips.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Brand Palette
BRAND_PRIMARY = "#38bdf8"    # Sky blue
BRAND_SECONDARY = "#818cf8"  # Indigo
BRAND_SUCCESS = "#34d399"    # Emerald
BRAND_WARNING = "#fbbf24"    # Amber
BRAND_DANGER = "#f87171"     # Rose
BG_COLOR = "rgba(15, 23, 42, 0.6)"
PAPER_COLOR = "rgba(0, 0, 0, 0)"

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=PAPER_COLOR,
    plot_bgcolor=PAPER_COLOR,
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#cbd5e1", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

AXIS_DEFAULTS = dict(
    gridcolor="rgba(255, 255, 255, 0.08)",
    zerolinecolor="rgba(255, 255, 255, 0.1)",
)


def plot_revenue_and_orders_trend(df: pd.DataFrame, granularity: str = "monthly") -> go.Figure:
    """Creates a dual-axis revenue and order volume trajectory chart."""
    x_col = "sales_month" if "sales_month" in df.columns else "sales_date"
    fig = go.Figure()

    # Revenue Line / Area
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df["total_revenue"],
            name="Net Revenue ($)",
            mode="lines+markers",
            line=dict(color=BRAND_PRIMARY, width=3),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.1)",
            hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
            yaxis="y1",
        )
    )

    # Order Volume Bar
    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df["total_orders"],
            name="Order Count",
            marker=dict(color="rgba(129, 140, 248, 0.4)", line=dict(color=BRAND_SECONDARY, width=1)),
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
            yaxis="y2",
        )
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="<b>Revenue & Order Volume Trajectory</b>",
        xaxis=dict(**AXIS_DEFAULTS),
        yaxis=dict(
            **AXIS_DEFAULTS,
            title="Revenue ($)",
            tickprefix="$",
            tickformat=",.0f",
        ),
        yaxis2=dict(
            title="Orders",
            overlaying="y",
            side="right",
            showgrid=False,
            tickformat=",.0f",
        ),
        hovermode="x unified",
        height=380,
    )
    return fig


def plot_category_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing revenue share by product category."""
    colors = [BRAND_PRIMARY, BRAND_SECONDARY, BRAND_SUCCESS, BRAND_WARNING, "#f472b6", "#a78bfa"]
    fig = px.pie(
        df,
        names="category",
        values="category_revenue",
        hole=0.55,
        color_discrete_sequence=colors,
        title="<b>Revenue Contribution by Category</b>",
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#0f172a", width=2)),
    )
    fig.update_layout(**LAYOUT_DEFAULTS, height=360)
    return fig


def plot_regional_performance(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart comparing regional revenue and AOV."""
    df_sorted = df.sort_values("total_revenue", ascending=True)
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df_sorted["region"],
            x=df_sorted["total_revenue"],
            orientation="h",
            name="Total Revenue",
            marker=dict(
                color=BRAND_PRIMARY,
                line=dict(color="#38bdf8", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="<b>Regional Revenue Contribution</b>",
        xaxis=dict(**AXIS_DEFAULTS, title="Net Revenue ($)", tickprefix="$", tickformat=",.0f"),
        yaxis=dict(**AXIS_DEFAULTS, title=""),
        height=360,
    )
    return fig


def plot_top_products(df: pd.DataFrame, title: str = "Top Products by Revenue") -> go.Figure:
    """Horizontal bar chart for top products."""
    df_sorted = df.sort_values("total_revenue", ascending=True).tail(10)
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df_sorted["product_name"],
            x=df_sorted["total_revenue"],
            orientation="h",
            marker=dict(
                color=BRAND_SECONDARY,
                line=dict(color="#a5b4fc", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=f"<b>{title}</b>",
        xaxis=dict(**AXIS_DEFAULTS, title="Revenue ($)", tickprefix="$", tickformat=",.0f"),
        yaxis=dict(**AXIS_DEFAULTS, title=""),
        height=380,
    )
    return fig


def plot_cohort_retention_heatmap(df: pd.DataFrame) -> go.Figure:
    """Builds an interactive cohort retention percentage heatmap matrix."""
    # Pivot into Cohort Month vs Month Offset
    pivot_df = df.pivot(index="cohort_month", columns="month_offset", values="retention_rate_pct")
    pivot_df = pivot_df.sort_index(ascending=True)

    # Columns up to Month 12 for clean viewing
    cols_to_keep = [c for c in pivot_df.columns if c <= 12]
    pivot_df = pivot_df[cols_to_keep]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=[f"M+{c}" for c in pivot_df.columns],
            y=pivot_df.index,
            colorscale="Viridis",
            zmin=0,
            zmax=100,
            text=[[f"{val:.1f}%" if not np.isnan(val) else "" for val in row] for row in pivot_df.values],
            texttemplate="%{text}",
            textfont=dict(size=10, color="#ffffff"),
            colorbar=dict(title="Retention %"),
            hovertemplate="<b>Cohort: %{y}</b><br>Period: %{x}<br>Retention: %{z:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="<b>Cohort Retention Matrix (% Retained Customers by Month Offset)</b>",
        xaxis=dict(title="Months After Acquisition", tickmode="linear"),
        yaxis=dict(title="Cohort Acquisition Month", autorange="reversed"),
        height=520,
    )
    return fig


def plot_returns_analysis(df: pd.DataFrame) -> go.Figure:
    """Bar chart breakdown of return reasons and refunded capital."""
    df_sorted = df.sort_values("total_returns", ascending=False)
    fig = px.bar(
        df_sorted,
        x="return_reason",
        y="total_returns",
        color="total_refunded",
        color_continuous_scale="Reds",
        title="<b>Return Volume and Value Loss by Reason</b>",
        labels={"total_returns": "Number of Returns", "return_reason": "Reason", "total_refunded": "Refund ($)"},
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Returns: %{y:,}<br>Refunds: $%{marker.color:,.2f}<extra></extra>"
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis=dict(**AXIS_DEFAULTS),
        yaxis=dict(**AXIS_DEFAULTS),
        height=360,
    )
    return fig
