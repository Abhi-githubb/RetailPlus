"""
RetailPulse Master ETL & Data Pipeline Orchestrator.
Executes the end-to-end data lifecycle:
1. Synthetic generation (100k+ orders, 20k+ customers, 500+ products)
2. Schema & data quality validation + anomaly auditing
3. Feature engineering & business transformations
4. Relational database schema migration
5. High-performance batch data loading
6. Analytical views compilation
7. Post-load verification & executive pipeline summary report
"""

import sys
import time
from datetime import datetime
from pathlib import Path

from src.ingestion.synthetic_generator import generate_synthetic_data, save_raw_datasets
from src.validation.data_quality import DataQualityValidator
from src.transformation.cleaner import DataTransformer
from src.database.loader import DatabaseLoader
from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger

REQUIRED_DATASETS = ["customers", "products", "orders", "order_items", "payments", "returns"]


def run_full_pipeline(
    num_customers: int = 22000,
    num_products: int = 550,
    num_orders: int = 105000,
    skip_generation_if_exists: bool = False,
) -> bool:
    """Execute the complete RetailPulse ETL pipeline from generation through verification."""
    start_time = time.time()
    logger.info("==========================================================")
    logger.info("       RETAILPULSE E-COMMERCE ANALYTICS ETL PIPELINE       ")
    logger.info("==========================================================")
    logger.info(f"Pipeline Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # STEP 1: DATA INGESTION / GENERATION
        logger.info("[Step 1/6] Ingesting Raw E-Commerce Transaction Data...")
        raw_datasets = None

        if skip_generation_if_exists:
            processed_available = all(
                (PROCESSED_DATA_DIR / f"{table}_processed.csv").exists()
                and (PROCESSED_DATA_DIR / f"{table}_processed.csv").stat().st_size > 100
                for table in REQUIRED_DATASETS
            )
            if processed_available:
                logger.info("Existing processed datasets found; generation/validation will be skipped.")

        if raw_datasets is None and not (
            skip_generation_if_exists
            and all(
                (PROCESSED_DATA_DIR / f"{table}_processed.csv").exists()
                and (PROCESSED_DATA_DIR / f"{table}_processed.csv").stat().st_size > 100
                for table in REQUIRED_DATASETS
            )
        ):
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
            clean_datasets, quality_report = validator.validate_and_clean_all(raw_datasets)

            transformer = DataTransformer()
            transformed_datasets = transformer.transform_all(clean_datasets)
        else:
            # Existing processed files are already transformed and ready for loading.
            quality_report = None
            transformed_datasets = None

        logger.info("[OK] Step 1 Complete: Raw/processed datasets staged.")
        logger.info("[OK] Step 2 Complete: Data quality validation completed.")
        logger.info("[OK] Step 3 Complete: Analytical transformations completed.")

        # STEP 4: DATABASE SCHEMA
        loader = DatabaseLoader()
        logger.info("[Step 4/6] Initializing relational database schema...")
        loader.reset_and_create_schema()
        logger.info("[OK] Step 4 Complete: Database tables configured.")

        # STEP 5: LOAD
        logger.info("[Step 5/6] Loading all relational records...")
        inserted_counts = loader.load_clean_data(transformed_datasets)
        logger.info("[OK] Step 5 Complete: All relational records loaded.")

        # STEP 6: VIEWS + VERIFICATION
        logger.info("[Step 6/6] Deploying analytical views and verifying warehouse...")
        loader.create_analytical_views()
        verified_counts = loader.verify_database_counts()

        required_tables = ["customers", "products", "orders", "order_items", "payments", "returns"]
        required_views = [
            "daily_sales", "monthly_sales", "customer_metrics", "product_performance",
            "category_performance", "regional_performance", "retention_metrics",
            "cohort_analysis", "return_metrics",
        ]
        failed_tables = [name for name in required_tables if verified_counts.get(name, -1) <= 0]
        failed_views = [name for name in required_views if verified_counts.get(name, -1) < 0]
        if failed_tables:
            raise RuntimeError(f"Database verification failed for tables: {failed_tables}")
        if failed_views:
            raise RuntimeError(f"Database verification failed for views: {failed_views}")

        logger.info("[OK] Step 6 Complete: Analytical views deployed and warehouse verified.")

        elapsed = round(time.time() - start_time, 2)

        print("\n" + "=" * 65)
        print("         RETAILPULSE ETL EXECUTION SUMMARY REPORT        ")
        print("=" * 65)
        print("Status:                      SUCCESS")
        print(f"Execution Duration:          {elapsed} seconds")

        if quality_report is not None:
            print(f"Total Records Processed:     {quality_report.total_records_processed:,}")
            print(f"Duplicates Removed:          {quality_report.total_duplicates_removed:,}")
            print(f"Invalid Rows Quarantined:    {quality_report.total_invalid_quarantined:,}")
            print(f"Final Clean Records Loaded:  {quality_report.total_clean_records:,}")
            print("-" * 65)
            print("TABLE-BY-TABLE BREAKDOWN:")
            for tbl, metrics in quality_report.table_metrics.items():
                print(
                    f"  • {tbl.ljust(14)}: Raw={metrics['total_raw_rows']:,} | "
                    f"Dups={metrics['duplicates_removed']} | "
                    f"Quarantine={metrics['invalid_rows_quarantined']} | "
                    f"Clean={metrics['clean_rows_retained']:,}"
                )
        else:
            print("Existing processed datasets loaded successfully.")

        print("-" * 65)
        print("DATA WAREHOUSE ROW VERIFICATION:")
        for entity in required_tables:
            print(f"  • {entity.ljust(22)}: {verified_counts[entity]:,} records")
        print("=" * 65 + "\n")

        logger.info("RetailPulse ETL Pipeline completed with 100% success.")
        return True

    except Exception as e:
        logger.critical(f"Pipeline execution aborted due to unhandled exception: {e}", exc_info=True)
        print(f"\n[ERROR] ETL Pipeline Failed: {e}\n", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)
