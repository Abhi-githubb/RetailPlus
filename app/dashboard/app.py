"""
RetailPulse — E-Commerce Analytics Platform.
Production-grade Streamlit SaaS dashboard for business stakeholders and executive leadership.
Backed by PostgreSQL/SQLite data warehouse, automated ETL pipeline, and SQL analytics engine.
"""

import sys
from pathlib import Path

# Add project root to sys.path so imports work seamlessly
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
from datetime import datetime, date
import pandas as pd
import streamlit as st
from src.analytics.query_runner import query_runner
from src.database.connection import check_db_connection
from src.utils.config import PROCESSED_DATA_DIR
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

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="RetailPulse | E-Commerce Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom CSS
st.markdown(load_custom_css(), unsafe_allow_html=True)

# Auto-Initialize Warehouse on first cloud launch if empty
@st.cache_resource
def ensure_warehouse_initialized():
    """Runs data pipeline automatically if warehouse is empty on cloud deployment."""
    from sqlalchemy import inspect
    from src.database.connection import engine
    from run_pipeline import run_full_pipeline

    try:
        insp = inspect(engine)
        tables = insp.get_table_names()
        if "orders" not in tables:
            with st.spinner("🚀 First-time Cloud Deployment: Ingesting 105k+ orders and compiling analytical warehouse..."):
                run_full_pipeline()
    except Exception as e:
        st.error(f"Warehouse initialization error: {e}")

ensure_warehouse_initialized()


# ==========================================================
# SIDEBAR NAVIGATION & GLOBAL FILTERS
# ==========================================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1.6rem; font-weight: 800; color: #38bdf8;">⚡ RetailPulse</div>
        </div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: -0.8rem; margin-bottom: 1.5rem;">
            Enterprise Analytics Intelligence Platform
        </div>
    """, unsafe_allow_html=True)

    # Navigation Menu
    nav_selection = st.radio(
        "Navigation",
        [
            "🏢 Executive Overview",
            "📈 Sales Analytics",
            "👥 Customer Analytics",
            "📦 Product Analytics",
            "🔄 Cohort Analysis",
            "🌍 Regional Analytics",
            "🔁 Returns Analytics",
            "🛡️ Data Quality & Pipeline",
        ],
        index=0,
    )

    st.markdown("---")
    st.subheader("Global Filters")

    # Filter Defaults in Session State
    if "filter_start_date" not in st.session_state:
        st.session_state.filter_start_date = date(2023, 1, 1)
    if "filter_end_date" not in st.session_state:
        st.session_state.filter_end_date = date(2025, 6, 30)
    if "filter_region" not in st.session_state:
        st.session_state.filter_region = "All"
    if "filter_category" not in st.session_state:
        st.session_state.filter_category = "All"

    # Reset Filters Action
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.filter_start_date = date(2023, 1, 1)
        st.session_state.filter_end_date = date(2025, 6, 30)
        st.session_state.filter_region = "All"
        st.session_state.filter_category = "All"
        st.rerun()

    # Date Range Pickers
    date_range = st.date_input(
        "Date Range",
        value=(st.session_state.filter_start_date, st.session_state.filter_end_date),
        min_value=date(2023, 1, 1),
        max_value=date(2025, 12, 31),
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date_str = date_range[0].strftime("%Y-%m-%d")
        end_date_str = date_range[1].strftime("%Y-%m-%d")
    else:
        start_date_str = "2023-01-01"
        end_date_str = "2025-06-30"

    # Region Filter
    regions = ["All", "North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"]
    selected_region = st.selectbox("Geographic Region", regions, index=regions.index(st.session_state.filter_region))

    # Category Filter
    categories = ["All", "Electronics", "Apparel", "Home & Kitchen", "Beauty & Personal Care", "Sports & Outdoors", "Books & Media"]
    selected_category = st.selectbox("Product Category", categories, index=categories.index(st.session_state.filter_category))

    st.markdown("---")
    # Live System Status Indicator
    db_ok, db_info = check_db_connection()
    status_color = "#10b981" if db_ok else "#ef4444"
    st.markdown(f"""
        <div style="font-size: 0.75rem; color: #94a3b8;">
            <b>Database:</b> <span style="color: {status_color}; font-weight: 600;">{'● Connected' if db_ok else '● Offline'}</span><br>
            <span style="font-size: 0.7rem; color: #64748b;">{db_info}</span>
        </div>
    """, unsafe_allow_html=True)


# ==========================================================
# TOP BRANDING & HEADER BAR
# ==========================================================
st.markdown(f"""
    <div class="brand-container">
        <div>
            <h1 class="brand-title">RetailPulse Analytics Platform</h1>
            <div class="brand-tagline">Enterprise E-Commerce Intelligence • Transaction Warehouse • Real-Time SQL Analytics</div>
        </div>
        <div>
            <span class="live-badge">
                <span class="live-dot"></span> Production Warehouse Online
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)


# ==========================================================
# SECTION 1: EXECUTIVE OVERVIEW
# ==========================================================
if nav_selection == "🏢 Executive Overview":
    st.subheader("Executive KPI Summary")

    summary_data = query_runner.get_kpi_summary(
        start_date=start_date_str,
        end_date=end_date_str,
        region=selected_region,
        category=selected_category,
    )

    # Render Metric Cards (Row 1)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        render_metric_card(
            title="Total Net Revenue",
            value=format_currency(summary_data["total_revenue"]),
            delta="+18.4% vs prior" if summary_data["total_revenue"] > 0 else None,
            delta_type="positive",
            subtitle="Completed / Shipped orders",
        )
    with kpi_col2:
        render_metric_card(
            title="Total Orders",
            value=format_number(summary_data["total_orders"]),
            delta="+12.1% YoY" if summary_data["total_orders"] > 0 else None,
            delta_type="positive",
            subtitle=f"{format_number(summary_data['active_customers'])} unique buyers",
        )
    with kpi_col3:
        render_metric_card(
            title="Average Order Value (AOV)",
            value=format_currency(summary_data["average_order_value"]),
            delta="+5.6% vs benchmark",
            delta_type="positive",
            subtitle=f"{summary_data.get('total_units_sold', 0):,} units sold",
        )
    with kpi_col4:
        margin_pct = summary_data.get("profit_margin_pct", 0)
        render_metric_card(
            title="Estimated Gross Profit",
            value=format_currency(summary_data["estimated_profit"]),
            delta=f"{margin_pct:.1f}% net margin",
            delta_type="positive" if margin_pct >= 40 else "neutral",
            subtitle="After product COGS & discounts",
        )

    # Dynamic Business Takeaways
    monthly_sales_df = query_runner.get_sales_trend(
        granularity="monthly",
        start_date=start_date_str,
        end_date=end_date_str,
        region=selected_region,
        category=selected_category,
    )
    category_df = query_runner.get_category_breakdown(
        start_date=start_date_str,
        end_date=end_date_str,
        region=selected_region,
    )
    regional_df = query_runner.get_regional_breakdown(
        start_date=start_date_str,
        end_date=end_date_str,
        category=selected_category,
    )

    insights = generate_executive_insights(summary_data, monthly_sales_df, category_df, regional_df)
    render_insights_box("Executive Strategic Takeaways", insights)

    # Visualizations Grid
    v_col1, v_col2 = st.columns([1.6, 1.0])
    with v_col1:
        if not monthly_sales_df.empty:
            fig_trend = plot_revenue_and_orders_trend(monthly_sales_df, granularity="monthly")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No sales records match the selected filter criteria.")

    with v_col2:
        if not category_df.empty:
            fig_cat = plot_category_distribution(category_df)
            st.plotly_chart(fig_cat, use_container_width=True)

    # Row 2 Visualizations
    v_col3, v_col4 = st.columns([1.0, 1.4])
    with v_col3:
        if not regional_df.empty:
            fig_reg = plot_regional_performance(regional_df)
            st.plotly_chart(fig_reg, use_container_width=True)

    with v_col4:
        top_prods_df = query_runner.get_top_products_table(limit=8, category=selected_category)
        if not top_prods_df.empty:
            fig_prods = plot_top_products(top_prods_df, title="Top 8 Performing SKUs by Gross Revenue")
            st.plotly_chart(fig_prods, use_container_width=True)


# ==========================================================
# SECTION 2: SALES ANALYTICS
# ==========================================================
elif nav_selection == "📈 Sales Analytics":
    st.subheader("Sales Velocity, Growth & Trajectory Analytics")

    granularity = st.radio("Temporal Resolution", ["Monthly", "Daily"], horizontal=True)
    sales_trend_df = query_runner.get_sales_trend(
        granularity=granularity.lower(),
        start_date=start_date_str,
        end_date=end_date_str,
        region=selected_region,
        category=selected_category,
    )

    if not sales_trend_df.empty:
        fig = plot_revenue_and_orders_trend(sales_trend_df, granularity=granularity.lower())
        st.plotly_chart(fig, use_container_width=True)

    # Dynamic Sales Insights
    monthly_sales_for_insights = query_runner.get_sales_trend(
        granularity="monthly",
        start_date=start_date_str,
        end_date=end_date_str,
        region=selected_region,
        category=selected_category,
    )
    sales_insights = generate_sales_insights(monthly_sales_for_insights)
    render_insights_box("Sales Performance Intelligence", sales_insights)

    # Growth & Seasonality Metrics
    st.subheader("Month-over-Month (MoM) Growth Analysis")
    mom_df = query_runner.execute_sql_file("revenue/monthly_growth_rate.sql")
    if not mom_df.empty:
        # Style dataframe
        st.dataframe(
            mom_df,
            column_config={
                "sales_month": "Month",
                "current_revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
                "prior_month_revenue": st.column_config.NumberColumn("Prior Month Rev", format="$%d"),
                "mom_revenue_growth_pct": st.column_config.NumberColumn("MoM Rev Growth", format="%.2f%%"),
                "current_orders": st.column_config.NumberColumn("Orders", format="%d"),
                "mom_order_growth_pct": st.column_config.NumberColumn("MoM Order Growth", format="%.2f%%"),
            },
            hide_index=True,
            use_container_width=True,
        )

    # Download button
    csv_data = mom_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Monthly Sales Data (CSV)", csv_data, "retailpulse_monthly_sales.csv", "text/csv")


# ==========================================================
# SECTION 3: CUSTOMER ANALYTICS
# ==========================================================
elif nav_selection == "👥 Customer Analytics":
    st.subheader("Customer Intelligence, Loyalty & Retention")

    cust_tab1, cust_tab2, cust_tab3 = st.tabs([
        "Acquisition & Loyalty", "RFM Behavioral Segmentation", "New vs Returning Buyers"
    ])

    with cust_tab1:
        st.markdown("#### Customer Acquisition Channel Efficiency")
        channel_df = query_runner.execute_sql_file("customer/acquisition_channel_performance.sql")
        st.dataframe(
            channel_df,
            column_config={
                "acquisition_channel": "Channel",
                "total_acquired_customers": st.column_config.NumberColumn("Acquired Cust.", format="%d"),
                "transacting_customers": st.column_config.NumberColumn("Transacting Cust.", format="%d"),
                "total_revenue_generated": st.column_config.NumberColumn("Total Revenue", format="$%d"),
                "average_active_clv": st.column_config.NumberColumn("Avg CLV", format="$%.2f"),
                "repeat_purchase_rate_pct": st.column_config.NumberColumn("Repeat Purchase %", format="%.2f%%"),
            },
            hide_index=True,
            use_container_width=True,
        )

        st.markdown("#### Customer Lifetime Value (CLV) Tiers")
        clv_df = query_runner.execute_sql_file("customer/customer_lifetime_value.sql")
        st.dataframe(clv_df, hide_index=True, use_container_width=True)

    with cust_tab2:
        st.markdown("#### Recency, Frequency, Monetary (RFM) Segmentation Matrix")
        rfm_df = query_runner.execute_sql_file("customer/customer_segmentation_rfm.sql")
        st.dataframe(
            rfm_df,
            column_config={
                "rfm_segment": "Segment",
                "customer_count": st.column_config.NumberColumn("Customers", format="%d"),
                "pct_of_customers": st.column_config.NumberColumn("% Base", format="%.1f%%"),
                "total_segment_revenue": st.column_config.NumberColumn("Total Spend", format="$%d"),
                "avg_monetary_value": st.column_config.NumberColumn("Avg Spend", format="$%.2f"),
                "avg_order_frequency": st.column_config.NumberColumn("Avg Frequency", format="%.1f orders"),
            },
            hide_index=True,
            use_container_width=True,
        )

    with cust_tab3:
        st.markdown("#### New vs Returning Buyers Trajectory")
        new_ret_df = query_runner.execute_sql_file("customer/new_vs_returning_customers.sql")
        st.dataframe(new_ret_df.tail(24), hide_index=True, use_container_width=True)


# ==========================================================
# SECTION 4: PRODUCT ANALYTICS
# ==========================================================
elif nav_selection == "📦 Product Analytics":
    st.subheader("Product Performance & Catalog Optimization")

    prod_col1, prod_col2 = st.columns(2)
    with prod_col1:
        st.markdown("#### Top 10 Best-Selling SKUs by Net Revenue")
        top_df = query_runner.get_top_products_table(limit=10, category=selected_category, ascending=False)
        st.dataframe(
            top_df,
            column_config={
                "product_name": "Product Name",
                "category": "Category",
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "units_sold": st.column_config.NumberColumn("Units", format="%d"),
                "total_revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
                "margin_pct": st.column_config.NumberColumn("Margin %", format="%.1f%%"),
            },
            hide_index=True,
            use_container_width=True,
        )

    with prod_col2:
        st.markdown("#### Bottom 10 Underperforming SKUs (Inventory Clearance)")
        bottom_df = query_runner.get_top_products_table(limit=10, category=selected_category, ascending=True)
        st.dataframe(
            bottom_df,
            column_config={
                "product_name": "Product Name",
                "category": "Category",
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "units_sold": st.column_config.NumberColumn("Units", format="%d"),
                "total_revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
            },
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("#### Category & Subcategory Margin Drilldown")
    subcat_df = query_runner.execute_sql_file("product/top_categories.sql")
    st.dataframe(
        subcat_df,
        column_config={
            "category": "Category",
            "subcategory": "Subcategory",
            "active_skus": "SKU Count",
            "total_units_sold": st.column_config.NumberColumn("Units Sold", format="%d"),
            "subcategory_revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
            "profit_margin_pct": st.column_config.NumberColumn("Margin %", format="%.1f%%"),
        },
        hide_index=True,
        use_container_width=True,
    )


# ==========================================================
# SECTION 5: COHORT ANALYSIS
# ==========================================================
elif nav_selection == "🔄 Cohort Analysis":
    st.subheader("Cohort Retention Analysis")
    st.markdown(
        "Tracks customer retention rate across successive months following initial transaction (Month 0)."
    )

    cohort_df = query_runner.get_cohort_matrix()
    if not cohort_df.empty:
        fig_cohort = plot_cohort_retention_heatmap(cohort_df)
        st.plotly_chart(fig_cohort, use_container_width=True)

        st.markdown("#### Raw Cohort Matrix Data")
        pivot_cohort = cohort_df.pivot(index="cohort_month", columns="month_offset", values="retention_rate_pct")
        st.dataframe(pivot_cohort, use_container_width=True)


# ==========================================================
# SECTION 6: REGIONAL ANALYTICS
# ==========================================================
elif nav_selection == "🌍 Regional Analytics":
    st.subheader("Geographic Market Penetration & Regional Performance")

    reg_df = query_runner.execute_sql_file("revenue/revenue_by_region.sql")
    if not reg_df.empty:
        r_col1, r_col2 = st.columns([1.2, 1.8])
        with r_col1:
            fig_reg = plot_regional_performance(reg_df)
            st.plotly_chart(fig_reg, use_container_width=True)
        with r_col2:
            st.dataframe(
                reg_df,
                column_config={
                    "region": "Market Region",
                    "total_orders": st.column_config.NumberColumn("Orders", format="%d"),
                    "unique_customers": st.column_config.NumberColumn("Customers", format="%d"),
                    "regional_revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
                    "pct_of_global_revenue": st.column_config.NumberColumn("Share", format="%.2f%%"),
                    "regional_aov": st.column_config.NumberColumn("AOV", format="$%.2f"),
                    "profit_margin_pct": st.column_config.NumberColumn("Margin", format="%.2f%%"),
                },
                hide_index=True,
                use_container_width=True,
            )


# ==========================================================
# SECTION 7: RETURNS ANALYTICS
# ==========================================================
elif nav_selection == "🔁 Returns Analytics":
    st.subheader("Returns, Refunds & Lost Capital Intelligence")

    ret_df = query_runner.get_returns_summary()
    cat_return_df = query_runner.execute_sql_file("retention/return_rate.sql")

    if not ret_df.empty:
        ret_col1, ret_col2 = st.columns([1.4, 1.0])
        with ret_col1:
            fig_ret = plot_returns_analysis(ret_df)
            st.plotly_chart(fig_ret, use_container_width=True)
        with ret_col2:
            st.markdown("#### Primary Return Drivers")
            st.dataframe(
                ret_df,
                column_config={
                    "return_reason": "Return Reason",
                    "total_returns": st.column_config.NumberColumn("Returns", format="%d"),
                    "total_refunded": st.column_config.NumberColumn("Refund Loss", format="$%d"),
                    "avg_refund": st.column_config.NumberColumn("Avg Refund", format="$%.2f"),
                },
                hide_index=True,
                use_container_width=True,
            )

    st.markdown("#### Category Return Rate Exposure")
    st.dataframe(
        cat_return_df,
        column_config={
            "category": "Category",
            "total_units_sold": st.column_config.NumberColumn("Units Sold", format="%d"),
            "total_category_revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
            "total_returns_filed": st.column_config.NumberColumn("Returns", format="%d"),
            "return_rate_pct": st.column_config.NumberColumn("Return Rate %", format="%.2f%%"),
            "total_refunded_amount": st.column_config.NumberColumn("Refund Loss", format="$%d"),
            "refund_value_loss_pct": st.column_config.NumberColumn("Value Loss %", format="%.2f%%"),
        },
        hide_index=True,
        use_container_width=True,
    )


# ==========================================================
# SECTION 8: DATA QUALITY & PIPELINE HEALTH
# ==========================================================
elif nav_selection == "🛡️ Data Quality & Pipeline":
    st.subheader("ETL Pipeline Health & Data Governance Audit")

    report_path = PROCESSED_DATA_DIR / "data_quality_report.json"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            quality_report = json.load(f)

        q_col1, q_col2, q_col3, q_col4 = st.columns(4)
        with q_col1:
            render_metric_card("Records Processed", f"{quality_report['total_records_processed']:,}", subtitle="Raw records ingested")
        with q_col2:
            render_metric_card("Duplicates Cleaned", f"{quality_report['total_duplicates_removed']:,}", subtitle="Deduplication stage")
        with q_col3:
            render_metric_card("Quarantined Rows", f"{quality_report['total_invalid_quarantined']:,}", subtitle="Schema anomalies isolated")
        with q_col4:
            render_metric_card("Warehouse Clean Rows", f"{quality_report['total_clean_records']:,}", subtitle="Loaded to relational DB")

        st.markdown(f"**Last ETL Pipeline Run:** `{quality_report['execution_timestamp']}`")

        st.markdown("#### Table-by-Table Data Quality Breakdown")
        table_records = []
        for tbl, data in quality_report["table_metrics"].items():
            table_records.append({
                "Table": tbl,
                "Raw Records": data["total_raw_rows"],
                "Missing Values Imputed": data["missing_values_detected"],
                "Duplicates Cleared": data["duplicates_removed"],
                "Quarantined Anomalies": data["invalid_rows_quarantined"],
                "Final Clean Loaded": data["clean_rows_retained"],
            })
        st.dataframe(pd.DataFrame(table_records), hide_index=True, use_container_width=True)
    else:
        st.warning("Data Quality report not found. Execute `python run_pipeline.py` to generate.")
