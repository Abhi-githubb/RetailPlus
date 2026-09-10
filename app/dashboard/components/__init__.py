"""Dashboard components package."""
from app.dashboard.components.styles import load_custom_css
from app.dashboard.components.kpi_cards import render_metric_card, format_currency, format_number
from app.dashboard.components.charts import (
    plot_revenue_and_orders_trend,
    plot_category_distribution,
    plot_regional_performance,
    plot_top_products,
    plot_cohort_retention_heatmap,
    plot_returns_analysis,
)
from app.dashboard.components.insights import (
    generate_executive_insights,
    generate_sales_insights,
    generate_customer_insights,
    render_insights_box,
)

__all__ = [
    "load_custom_css",
    "render_metric_card",
    "format_currency",
    "format_number",
    "plot_revenue_and_orders_trend",
    "plot_category_distribution",
    "plot_regional_performance",
    "plot_top_products",
    "plot_cohort_retention_heatmap",
    "plot_returns_analysis",
    "generate_executive_insights",
    "generate_sales_insights",
    "generate_customer_insights",
    "render_insights_box",
]
