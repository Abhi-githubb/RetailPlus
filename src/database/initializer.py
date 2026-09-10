"""
Robust Database Initialization and Verification Engine for RetailPulse.
Guarantees that required relational tables and analytical views are created,
verified, and populated with data before any dashboard or API query executes.
Safe for concurrent runs and idempotent across PostgreSQL and SQLite.
"""

import re
import traceback
from typing import Any, Dict, List, Tuple
import pandas as pd
from sqlalchemy import inspect, text

from src.utils.logger import logger
from src.utils.config import BASE_DIR, PROCESSED_DATA_DIR, DATABASE_URL
from src.database.connection import engine, Base
from src.database.loader import DatabaseLoader
from src.ingestion.synthetic_generator import generate_synthetic_data, save_raw_datasets
from src.validation.data_quality import DataQualityValidator
from src.transformation.cleaner import DataTransformer

REQUIRED_TABLES: List[str] = [
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "returns",
]

REQUIRED_VIEWS: List[str] = [
    "daily_sales",
    "monthly_sales",
    "customer_metrics",
    "product_performance",
    "category_performance",
    "regional_performance",
    "retention_metrics",
    "cohort_analysis",
    "return_metrics",
]


def redact_db_url(url: str) -> str:
    """Masks credentials in database URL for safe display in diagnostics."""
    if not url:
        return "Not configured"
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", url)


def inspect_warehouse_state() -> Tuple[Dict[str, int], List[str]]:
    """Inspects required tables and analytical views on the same shared engine used by queries."""
    table_counts = {}
    with engine.connect() as conn:
        for tbl in REQUIRED_TABLES:
            try:
                cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                table_counts[tbl] = int(cnt) if cnt is not None else 0
            except Exception:
                table_counts[tbl] = -1

    failed_views = []
    with engine.connect() as conn:
        for view_name in REQUIRED_VIEWS:
            try:
                conn.execute(text(f"SELECT 1 FROM {view_name} LIMIT 1"))
            except Exception:
                failed_views.append(view_name)

    return table_counts, failed_views


def initialize_database(
    force: bool = False,
    num_orders: int = 105000,
    num_customers: int = 22000,
    num_products: int = 550,
) -> Dict[str, Any]:
    """
    Initializes and verifies the warehouse before dashboard queries run.
    Uses the exact same shared SQLAlchemy engine as the query runner.
    """
    dialect = engine.dialect.name
    redacted_url = redact_db_url(DATABASE_URL)
    logger.info(f"Checking RetailPulse warehouse state on {dialect} ({redacted_url})...")

    try:
        insp = inspect(engine)
        existing_tables = set(insp.get_table_names())
        tables_exist = all(tbl in existing_tables for tbl in REQUIRED_TABLES)

        if tables_exist and not force:
            table_counts, failed_views = inspect_warehouse_state()
            orders_count = table_counts.get("orders", 0)

            if orders_count > 0 and all(c > 0 for c in table_counts.values()):
                if failed_views:
                    logger.warning(f"Repairing {len(failed_views)} broken/missing views: {failed_views}")
                    loader = DatabaseLoader()
                    loader.create_analytical_views()
                    _, still_failed = inspect_warehouse_state()
                    if still_failed:
                        raise RuntimeError(f"Analytical views failed to compile: {still_failed}")

                logger.info(f"Warehouse already initialized ({dialect}): {orders_count:,} orders present.")
                return {
                    "success": True,
                    "status": "ready",
                    "dialect": dialect,
                    "db_url_redacted": redacted_url,
                    "tables": table_counts,
                    "views_verified": REQUIRED_VIEWS,
                    "message": f"Warehouse active with {orders_count:,} orders and 9 verified views.",
                }

        logger.info(f"Initializing warehouse schema and loading dataset on {dialect}...")
        loader = DatabaseLoader()
        loader.reset_and_create_schema()

        clean_datasets = {}
        csvs_available = True
        for tbl in REQUIRED_TABLES:
            p = PROCESSED_DATA_DIR / f"{tbl}_processed.csv"
            if not p.exists() or p.stat().st_size < 100:
                csvs_available = False
                break

        if csvs_available:
            logger.info("Found existing processed datasets in data/processed/. Loading directly...")
            loader.load_clean_data()
        else:
            logger.info("Generating synthetic transactions and executing ETL pipeline...")
            raw_datasets = generate_synthetic_data(
                num_customers=num_customers,
                num_products=num_products,
                num_orders=num_orders,
                start_date="2023-01-01",
                end_date="2025-06-30",
                inject_anomalies=True,
            )
            save_raw_datasets(raw_datasets)

            validator = DataQualityValidator()
            clean_data, _ = validator.validate_and_clean_all(raw_datasets)
            transformer = DataTransformer()
            transformed_data = transformer.transform_all(clean_data)
            loader.load_clean_data(transformed_data)

        logger.info("Deploying analytical views from views.sql...")
        loader.create_analytical_views()

        table_counts, failed_views = inspect_warehouse_state()
        for tbl in REQUIRED_TABLES:
            cnt = table_counts.get(tbl, -1)
            if cnt <= 0:
                raise RuntimeError(f"Table verification failed: table '{tbl}' has {cnt} rows.")

        if failed_views:
            raise RuntimeError(f"View verification failed: views {failed_views} could not be queried.")

        logger.info(f"✓ All {len(REQUIRED_TABLES)} tables and {len(REQUIRED_VIEWS)} analytical views verified.")

        return {
            "success": True,
            "status": "initialized",
            "dialect": dialect,
            "db_url_redacted": redacted_url,
            "tables": table_counts,
            "views_verified": REQUIRED_VIEWS,
            "message": f"Successfully initialized and verified {len(REQUIRED_TABLES)} tables and {len(REQUIRED_VIEWS)} views.",
        }

    except Exception as e:
        err_tb = traceback.format_exc()
        logger.critical(f"Database initialization failed: {e}\n{err_tb}")
        return {
            "success": False,
            "error": str(e),
            "traceback": err_tb,
            "dialect": dialect,
            "db_url_redacted": redacted_url,
        }
