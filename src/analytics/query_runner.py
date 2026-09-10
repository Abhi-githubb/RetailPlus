"""
SQL Analytics Engine and Query Runner for RetailPulse.
Executes modular SQL analytics queries, applies dynamic filters,
and formats dataframes for FastAPI and Streamlit.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import text
from src.database.connection import engine
from src.utils.logger import logger
from src.utils.config import SQL_DIR


class QueryRunner:
    """Loads and executes SQL queries from the sql/ repository."""

    def __init__(self):
        self.engine = engine
        self.sql_dir = SQL_DIR

    def execute_raw_sql(self, sql_query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Executes an inline SQL statement and returns a Pandas DataFrame."""
        with self.engine.connect() as conn:
            df = pd.read_sql(text(sql_query), con=conn, params=params or {})
        return df

    def execute_sql_file(self, relative_path: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Loads and executes an SQL file by relative path from sql/."""
        filepath = self.sql_dir / relative_path
        if not filepath.exists():
            raise FileNotFoundError(f"SQL file not found at: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            sql_query = f.read()

        return self.execute_raw_sql(sql_query, params)

    def get_kpi_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        region: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculates executive high-level KPIs with optional global filters."""
        where_clauses = ["o.order_status IN ('Completed', 'Shipped')"]
        params: Dict[str, Any] = {}

        if start_date:
            where_clauses.append("o.order_date >= :start_date")
            params["start_date"] = f"{start_date} 00:00:00"
        if end_date:
            where_clauses.append("o.order_date <= :end_date")
            params["end_date"] = f"{end_date} 23:59:59"
        if region and region != "All":
            where_clauses.append("o.shipping_region = :region")
            params["region"] = region
        if category and category != "All":
            where_clauses.append("p.category = :category")
            params["category"] = category

        where_sql = " AND ".join(where_clauses)

        query = f"""
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS active_customers,
            COALESCE(ROUND(SUM(oi.net_amount), 2), 0.0) AS total_revenue,
            COALESCE(ROUND(AVG(o.total_amount), 2), 0.0) AS average_order_value,
            COALESCE(ROUND(SUM(oi.profit), 2), 0.0) AS estimated_profit,
            COALESCE(ROUND(SUM(oi.discount), 2), 0.0) AS total_discounts,
            COALESCE(SUM(oi.quantity), 0) AS total_units_sold
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE {where_sql};
        """
        df = self.execute_raw_sql(query, params)
        if df.empty:
            return {
                "total_orders": 0,
                "active_customers": 0,
                "total_revenue": 0.0,
                "average_order_value": 0.0,
                "estimated_profit": 0.0,
                "profit_margin_pct": 0.0,
                "total_units_sold": 0,
            }

        row = df.iloc[0].to_dict()
        rev = float(row["total_revenue"])
        profit = float(row["estimated_profit"])
        margin = round((profit / rev * 100), 2) if rev > 0 else 0.0
        row["profit_margin_pct"] = margin

        # Get return rate in same scope
        ret_query = f"""
        SELECT
            COUNT(DISTINCT r.return_id) AS return_count,
            COALESCE(ROUND(SUM(r.refund_amount), 2), 0.0) AS total_refunded
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN returns r ON oi.order_id = r.order_id AND oi.product_id = r.product_id
        WHERE {where_sql};
        """
        ret_df = self.execute_raw_sql(ret_query, params)
        ret_count = int(ret_df.iloc[0]["return_count"]) if not ret_df.empty else 0
        total_units = int(row["total_units_sold"]) if row["total_units_sold"] else 1
        return_rate = round((ret_count * 100.0 / total_units), 2) if total_units > 0 else 0.0

        row["total_returns"] = ret_count
        row["return_rate_pct"] = return_rate
        row["total_refunded"] = float(ret_df.iloc[0]["total_refunded"]) if not ret_df.empty else 0.0

        return row

    def get_sales_trend(
        self,
        granularity: str = "monthly",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        region: Optional[str] = None,
        category: Optional[str] = None,
    ) -> pd.DataFrame:
        """Extracts sales trends grouped by day or month."""
        date_expr = "SUBSTR(o.order_date, 1, 7)" if granularity == "monthly" else "SUBSTR(o.order_date, 1, 10)"
        col_name = "sales_month" if granularity == "monthly" else "sales_date"

        where_clauses = ["o.order_status IN ('Completed', 'Shipped')"]
        params: Dict[str, Any] = {}

        if start_date:
            where_clauses.append("o.order_date >= :start_date")
            params["start_date"] = f"{start_date} 00:00:00"
        if end_date:
            where_clauses.append("o.order_date <= :end_date")
            params["end_date"] = f"{end_date} 23:59:59"
        if region and region != "All":
            where_clauses.append("o.shipping_region = :region")
            params["region"] = region
        if category and category != "All":
            where_clauses.append("p.category = :category")
            params["category"] = category

        where_sql = " AND ".join(where_clauses)

        query = f"""
        SELECT
            {date_expr} AS {col_name},
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS active_customers,
            ROUND(SUM(oi.net_amount), 2) AS total_revenue,
            ROUND(AVG(o.total_amount), 2) AS average_order_value,
            ROUND(SUM(oi.profit), 2) AS total_profit
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE {where_sql}
        GROUP BY {date_expr}
        ORDER BY {col_name} ASC;
        """
        return self.execute_raw_sql(query, params)

    def get_category_breakdown(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        region: Optional[str] = None,
    ) -> pd.DataFrame:
        """Returns revenue, units, and margin broken down by category."""
        where_clauses = ["o.order_status IN ('Completed', 'Shipped')"]
        params: Dict[str, Any] = {}
        if start_date:
            where_clauses.append("o.order_date >= :start_date")
            params["start_date"] = f"{start_date} 00:00:00"
        if end_date:
            where_clauses.append("o.order_date <= :end_date")
            params["end_date"] = f"{end_date} 23:59:59"
        if region and region != "All":
            where_clauses.append("o.shipping_region = :region")
            params["region"] = region

        where_sql = " AND ".join(where_clauses)

        query = f"""
        SELECT
            p.category,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.net_amount), 2) AS category_revenue,
            ROUND(SUM(oi.profit), 2) AS category_profit,
            ROUND((SUM(oi.profit) / NULLIF(SUM(oi.net_amount), 0)) * 100.0, 2) AS margin_pct
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE {where_sql}
        GROUP BY p.category
        ORDER BY category_revenue DESC;
        """
        return self.execute_raw_sql(query, params)

    def get_regional_breakdown(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
    ) -> pd.DataFrame:
        """Returns revenue, orders, and AOV by geographic region."""
        where_clauses = ["o.order_status IN ('Completed', 'Shipped')"]
        params: Dict[str, Any] = {}
        if start_date:
            where_clauses.append("o.order_date >= :start_date")
            params["start_date"] = f"{start_date} 00:00:00"
        if end_date:
            where_clauses.append("o.order_date <= :end_date")
            params["end_date"] = f"{end_date} 23:59:59"
        if category and category != "All":
            where_clauses.append("p.category = :category")
            params["category"] = category

        where_sql = " AND ".join(where_clauses)

        query = f"""
        SELECT
            o.shipping_region AS region,
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS unique_customers,
            ROUND(SUM(oi.net_amount), 2) AS total_revenue,
            ROUND(AVG(o.total_amount), 2) AS average_order_value,
            ROUND(SUM(oi.profit), 2) AS total_profit
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE {where_sql}
        GROUP BY o.shipping_region
        ORDER BY total_revenue DESC;
        """
        return self.execute_raw_sql(query, params)

    def get_top_products_table(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        ascending: bool = False,
    ) -> pd.DataFrame:
        """Returns ranked best or worst performing products."""
        where_clauses = ["o.order_status IN ('Completed', 'Shipped')"]
        params: Dict[str, Any] = {"limit": limit}
        if category and category != "All":
            where_clauses.append("p.category = :category")
            params["category"] = category

        where_sql = " AND ".join(where_clauses)
        order_direction = "ASC" if ascending else "DESC"

        query = f"""
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            p.subcategory,
            p.price,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.net_amount), 2) AS total_revenue,
            ROUND(SUM(oi.profit), 2) AS total_profit,
            ROUND((SUM(oi.profit) / NULLIF(SUM(oi.net_amount), 0)) * 100.0, 2) AS margin_pct
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE {where_sql}
        GROUP BY p.product_id, p.product_name, p.category, p.subcategory, p.price
        ORDER BY total_revenue {order_direction}
        LIMIT :limit;
        """
        return self.execute_raw_sql(query, params)

    def get_cohort_matrix(self) -> pd.DataFrame:
        """Executes the cohort retention matrix query."""
        return self.execute_sql_file("cohorts/cohort_retention_matrix.sql")

    def get_returns_summary(self) -> pd.DataFrame:
        """Fetches return reason breakdown and impact."""
        query = """
        SELECT
            r.return_reason,
            COUNT(r.return_id) AS total_returns,
            ROUND(SUM(r.refund_amount), 2) AS total_refunded,
            ROUND(AVG(r.refund_amount), 2) AS avg_refund
        FROM returns r
        GROUP BY r.return_reason
        ORDER BY total_returns DESC;
        """
        return self.execute_raw_sql(query)


query_runner = QueryRunner()
