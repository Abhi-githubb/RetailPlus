"""
Dynamic Business Insights Generator for RetailPulse Dashboard.
Computes automated, data-driven narrative takeaways from actual database results.
No hardcoded text — all percentages, drivers, and trends are calculated on-the-fly.
"""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st


def generate_executive_insights(
    summary_data: Dict[str, Any],
    monthly_sales_df: pd.DataFrame,
    category_df: pd.DataFrame,
    regional_df: pd.DataFrame,
) -> List[str]:
    """Generates dynamic takeaways for the Executive Overview."""
    insights = []

    # 1. Period over period revenue trend
    if not monthly_sales_df.empty and len(monthly_sales_df) >= 2:
        last_month = monthly_sales_df.iloc[-1]
        prior_month = monthly_sales_df.iloc[-2]
        rev_change = ((last_month["total_revenue"] - prior_month["total_revenue"]) / prior_month["total_revenue"]) * 100
        direction = "increased" if rev_change >= 0 else "decreased"
        insights.append(
            f"Monthly revenue **{direction} by {abs(rev_change):.1f}%** from {prior_month['sales_month']} (${prior_month['total_revenue']:,.0f}) to {last_month['sales_month']} (${last_month['total_revenue']:,.0f})."
        )

    # 2. Dominant Category Contribution
    if not category_df.empty:
        top_cat = category_df.sort_values("category_revenue", ascending=False).iloc[0]
        total_rev = category_df["category_revenue"].sum()
        cat_share = (top_cat["category_revenue"] / total_rev * 100) if total_rev > 0 else 0
        insights.append(
            f"**{top_cat['category']}** is the largest product category, contributing **{cat_share:.1f}%** of gross revenue with an average margin of **{top_cat.get('margin_pct', 0):.1f}%**."
        )

    # 3. Leading Region & AOV
    if not regional_df.empty:
        top_region = regional_df.sort_values("total_revenue", ascending=False).iloc[0]
        highest_aov_region = regional_df.sort_values("average_order_value", ascending=False).iloc[0]
        insights.append(
            f"**{top_region['region']}** leads in total transaction volume, while **{highest_aov_region['region']}** commands the highest Average Order Value at **${highest_aov_region['average_order_value']:.2f}**."
        )

    # 4. Overall Health & Margin
    margin = summary_data.get("profit_margin_pct", 0)
    ret_rate = summary_data.get("return_rate_pct", 0)
    insights.append(
        f"Blended gross profit margin stands at **{margin:.1f}%**, with an overall return rate of **{ret_rate:.1f}%** across all fulfilled orders."
    )

    return insights


def generate_sales_insights(monthly_sales_df: pd.DataFrame) -> List[str]:
    """Generates analytical takeaways for the Sales Deep Dive."""
    insights = []
    if monthly_sales_df.empty:
        return ["No sales data available for the current filter scope."]

    # Peak Month
    peak_row = monthly_sales_df.sort_values("total_revenue", ascending=False).iloc[0]
    lowest_row = monthly_sales_df.sort_values("total_revenue", ascending=True).iloc[0]
    insights.append(
        f"Peak sales velocity occurred in **{peak_row['sales_month']}**, generating **${peak_row['total_revenue']:,.2f}** across **{peak_row['total_orders']:,}** orders."
    )

    # Average monthly run-rate
    avg_rev = monthly_sales_df["total_revenue"].mean()
    insights.append(
        f"The platform maintains an average monthly revenue run-rate of **${avg_rev:,.2f}**."
    )

    # Volatility / Seasonality
    spread = ((peak_row["total_revenue"] - lowest_row["total_revenue"]) / lowest_row["total_revenue"]) * 100
    insights.append(
        f"Revenue exhibits seasonal variance of **{spread:.1f}%** between peak and trough trading periods."
    )

    return insights


def generate_customer_insights(retention_df: pd.DataFrame, rfm_df: pd.DataFrame) -> List[str]:
    """Generates analytical takeaways for the Customer & Retention deep dive."""
    insights = []

    if not retention_df.empty and "repeat_purchase_rate_pct" in retention_df.columns:
        best_channel = retention_df.sort_values("repeat_purchase_rate_pct", ascending=False).iloc[0]
        insights.append(
            f"**{best_channel['acquisition_channel']}** delivers the highest customer loyalty, with a repeat purchase rate of **{best_channel['repeat_purchase_rate_pct']:.1f}%** and average CLV of **${best_channel['avg_clv']:.2f}**."
        )

    if not rfm_df.empty and "rfm_segment" in rfm_df.columns:
        champions = rfm_df[rfm_df["rfm_segment"] == "Champions"]
        if not champions.empty:
            champ_row = champions.iloc[0]
            insights.append(
                f"**Champions segment** represents **{champ_row['pct_of_customers']:.1f}%** of active buyers but drives **{champ_row.get('total_segment_revenue', 0):,.0f}** in cumulative spend."
            )

    return insights


def render_insights_box(title: str, insights: List[str]) -> None:
    """Renders a visually styled insight block in the Streamlit UI."""
    bullets = "".join([f"<li class='insight-text'>{insight}</li>" for insight in insights])
    html = f"""
    <div class="insight-box">
        <div class="insight-header">⚡ Automated Business Takeaways & Drivers</div>
        <ul style="margin: 0; padding-left: 1.25rem;">
            {bullets}
        </ul>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
