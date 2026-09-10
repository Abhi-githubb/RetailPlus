"""
Unit tests for RetailPulse Database connection, models, and analytical views.
"""

from sqlalchemy import text
from src.database.connection import engine, check_db_connection


def test_database_connectivity():
    is_ok, info = check_db_connection()
    assert is_ok is True
    assert "Connected successfully" in info


def test_core_tables_populated():
    with engine.connect() as conn:
        for tbl in ["customers", "products", "orders", "order_items", "payments", "returns"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            assert count > 0, f"Table {tbl} should not be empty"


def test_analytical_views_accessible():
    with engine.connect() as conn:
        for view in ["daily_sales", "monthly_sales", "customer_metrics", "product_performance", "category_performance", "regional_performance", "cohort_analysis"]:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar()
            assert res >= 0, f"View {view} should be queryable"
