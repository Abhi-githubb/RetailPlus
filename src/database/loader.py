"""
Database Schema Initialization and High-Performance Batch Data Loader.
Loads cleaned datasets into PostgreSQL/SQLite, handles idempotent table resets,
creates analytical views, and verifies row counts.
"""

from pathlib import Path
from typing import Dict
import pandas as pd
from sqlalchemy import text
from src.database.connection import engine, Base, is_sqlite
from src.database.models import Customer, Product, Order, OrderItem, Payment, Return
from src.utils.logger import logger
from src.utils.config import BASE_DIR, PROCESSED_DATA_DIR


class DatabaseLoader:
    """Handles schema creation, bulk data ingestion, and analytical view deployment."""

    def __init__(self):
        self.engine = engine

    def reset_and_create_schema(self) -> None:
        """Drops and recreates all relational tables according to ORM metadata."""
        logger.info("Initializing relational database schema...")
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        logger.info("Relational tables created successfully.")

    def load_clean_data(self, clean_datasets: Dict[str, pd.DataFrame] = None) -> Dict[str, int]:
        """
        Loads cleaned datasets into database tables in proper foreign-key order:
        1. customers
        2. products
        3. orders
        4. order_items
        5. payments
        6. returns
        """
        logger.info("Starting high-performance batch data loading...")

        if clean_datasets is None:
            clean_datasets = {}
            for tbl in ["customers", "products", "orders", "order_items", "payments", "returns"]:
                path = PROCESSED_DATA_DIR / f"{tbl}_processed.csv"
                if not path.exists():
                    raise FileNotFoundError(f"Processed dataset not found: {path}")
                clean_datasets[tbl] = pd.read_csv(path)

        inserted_counts = {}

        # 1. Customers
        logger.info(f"Loading customers ({len(clean_datasets['customers']):,} rows)...")
        clean_datasets["customers"].to_sql("customers", con=self.engine, if_exists="append", index=False, chunksize=10000)
        inserted_counts["customers"] = len(clean_datasets["customers"])

        # 2. Products
        logger.info(f"Loading products ({len(clean_datasets['products']):,} rows)...")
        clean_datasets["products"].to_sql("products", con=self.engine, if_exists="append", index=False, chunksize=5000)
        inserted_counts["products"] = len(clean_datasets["products"])

        # 3. Orders
        logger.info(f"Loading orders ({len(clean_datasets['orders']):,} rows)...")
        clean_datasets["orders"].to_sql("orders", con=self.engine, if_exists="append", index=False, chunksize=10000)
        inserted_counts["orders"] = len(clean_datasets["orders"])

        # 4. Order Items
        logger.info(f"Loading order_items ({len(clean_datasets['order_items']):,} rows)...")
        clean_datasets["order_items"].to_sql("order_items", con=self.engine, if_exists="append", index=False, chunksize=20000)
        inserted_counts["order_items"] = len(clean_datasets["order_items"])

        # 5. Payments
        logger.info(f"Loading payments ({len(clean_datasets['payments']):,} rows)...")
        clean_datasets["payments"].to_sql("payments", con=self.engine, if_exists="append", index=False, chunksize=20000)
        inserted_counts["payments"] = len(clean_datasets["payments"])

        # 6. Returns
        logger.info(f"Loading returns ({len(clean_datasets['returns']):,} rows)...")
        clean_datasets["returns"].to_sql("returns", con=self.engine, if_exists="append", index=False, chunksize=10000)
        inserted_counts["returns"] = len(clean_datasets["returns"])

        logger.info("Batch data loading finished successfully.")
        return inserted_counts

    def create_analytical_views(self) -> None:
        """Executes analytical views DDL script."""
        views_sql_path = BASE_DIR / "src" / "database" / "views.sql"
        if not views_sql_path.exists():
            logger.warning(f"Views SQL file not found at {views_sql_path}")
            return

        logger.info(f"Executing analytical views from {views_sql_path.name}...")
        with open(views_sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split statements by semicolon and execute each
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
        with self.engine.connect() as conn:
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    logger.error(f"Error creating view with statement: {stmt[:60]}... -> {e}")
            conn.commit()

        logger.info("All analytical views created successfully.")

    def verify_database_counts(self) -> Dict[str, int]:
        """Queries actual row counts for all relational and analytical views."""
        counts = {}
        tables_and_views = [
            "customers", "products", "orders", "order_items", "payments", "returns",
            "daily_sales", "monthly_sales", "customer_metrics", "product_performance",
            "category_performance", "regional_performance", "retention_metrics", "cohort_analysis", "return_metrics"
        ]
        with self.engine.connect() as conn:
            for name in tables_and_views:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar()
                    counts[name] = int(result)
                except Exception as e:
                    counts[name] = -1
                    logger.warning(f"Could not count {name}: {e}")
        return counts
