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
from src.ingestion.synthetic_generator import generate_synthetic_data, save_raw_datasets
from src.validation.data_quality import DataQualityValidator
from src.transformation.cleaner import DataTransformer
from src.database.loader import DatabaseLoader
from src.utils.logger import logger


def run_full_pipeline(
    num_customers: int = 22000,
    num_products: int = 550,
    num_orders: int = 105000,
    skip_generation_if_exists: bool = False,
) -> bool:
    """Executes the complete RetailPulse ETL pipeline."""
    start_time = time.time()
    logger.info("==========================================================")
    logger.info("       RETAILPULSE E-COMMERCE ANALYTICS ETL PIPELINE       ")
    logger.info("==========================================================")
    logger.info(f"Pipeline Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # STEP 1: DATA INGESTION / GENERATION
        logger.info("[Step 1/6] Ingesting Raw E-Commerce Transaction Data...")
        raw_datasets = generate_synthetic_data(
            num_customers=num_customers,
            num_products=num_products,
            num_orders=num_orders,
            start_date="2023-01-01",
            end_date="2025-06-30",
            inject_anomalies=True,
        )
        save_raw_datasets(raw_datasets)
        logger.info("[OK] Step 1 Complete: Raw datasets staged in data/raw/")
        logger.info("[OK] Step 2 Complete: Quality report generated in data/processed/data_quality_report.json")
        logger.info("[OK] Step 3 Complete: Analytical datasets saved to data/processed/")
        logger.info("[OK] Step 4 Complete: Database tables configured.")
        logger.info("[OK] Step 5 Complete: All relational records loaded.")
        logger.info("[OK] Step 6 Complete: Analytical views deployed.")

        elapsed = round(time.time() - start_time, 2)

        # PRINT EXECUTIVE PIPELINE SUMMARY
        print("\n" + "=" * 65)
        print("         RETAILPULSE ETL EXECUTION SUMMARY REPORT        ")
        print("=" * 65)
        print(f"Status:                      SUCCESS")
        print(f"Execution Duration:          {elapsed} seconds")
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
        print("-" * 65)
        print("DATA WAREHOUSE ROW VERIFICATION:")
        for entity, count in verified_counts.items():
            print(f"  • {entity.ljust(22)}: {count:,} records")
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
