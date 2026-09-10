"""
Unit tests for SQL analytics queries and metrics calculation.
"""

from src.analytics.query_runner import query_runner


def test_kpi_summary_calculation():
    kpis = query_runner.get_kpi_summary()
    assert kpis["total_orders"] > 50000
    assert kpis["total_revenue"] > 1000000.0
    assert kpis["average_order_value"] > 0
    assert kpis["profit_margin_pct"] > 0


def test_monthly_growth_rate_query():
    df = query_runner.execute_sql_file("revenue/monthly_growth_rate.sql")
    assert not df.empty
    assert "sales_month" in df.columns
    assert "mom_revenue_growth_pct" in df.columns


def test_cohort_retention_matrix_query():
    df = query_runner.execute_sql_file("cohorts/cohort_retention_matrix.sql")
    assert not df.empty
    assert "cohort_month" in df.columns
    assert "retention_rate_pct" in df.columns

    # Verify Month 0 retention is 100%
    month_0 = df[df["month_offset"] == 0]
    assert not month_0.empty
    assert (month_0["retention_rate_pct"] == 100.0).all()
