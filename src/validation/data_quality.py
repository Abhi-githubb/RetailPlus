"""
Data Quality and Validation Engine for RetailPulse.
Audits raw datasets against business rules, detects anomalies, removes duplicates,
quarantines invalid records, and generates an executive quality report.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Set, Tuple
import numpy as np
import pandas as pd
from src.utils.logger import logger
from src.utils.config import PROCESSED_DATA_DIR


@dataclass
class TableQualityMetric:
    table_name: str
    total_raw_rows: int = 0
    missing_values_detected: int = 0
    duplicates_removed: int = 0
    invalid_rows_quarantined: int = 0
    clean_rows_retained: int = 0
    anomalies_detected: List[str] = field(default_factory=list)


@dataclass
class PipelineQualityReport:
    execution_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_records_processed: int = 0
    total_duplicates_removed: int = 0
    total_invalid_quarantined: int = 0
    total_clean_records: int = 0
    table_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    passed_validation: bool = True


class DataQualityValidator:
    """Validates raw datasets, isolates anomalies, and produces quality metrics."""

    def __init__(self):
        self.report = PipelineQualityReport()

    def validate_and_clean_all(
        self, raw_datasets: Dict[str, pd.DataFrame]
    ) -> Tuple[Dict[str, pd.DataFrame], PipelineQualityReport]:
        """
        Executes full validation and cleaning pipeline across all tables.
        Returns cleaned dataframes and execution summary.
        """
        logger.info("--- Beginning Data Quality Audit & Schema Validation ---")
        clean_datasets = {}

        # 1. Customers
        clean_customers, cust_metric = self._validate_customers(raw_datasets["customers"])
        clean_datasets["customers"] = clean_customers
        self.report.table_metrics["customers"] = asdict(cust_metric)

        # 2. Products
        clean_products, prod_metric = self._validate_products(raw_datasets["products"])
        clean_datasets["products"] = clean_products
        self.report.table_metrics["products"] = asdict(prod_metric)

        # 3. Orders
        valid_cust_ids = set(clean_customers["customer_id"])
        clean_orders, order_metric = self._validate_orders(raw_datasets["orders"], valid_cust_ids)
        clean_datasets["orders"] = clean_orders
        self.report.table_metrics["orders"] = asdict(order_metric)

        # 4. Order Items
        valid_order_ids = set(clean_orders["order_id"])
        valid_prod_ids = set(clean_products["product_id"])
        clean_items, item_metric = self._validate_order_items(
            raw_datasets["order_items"], valid_order_ids, valid_prod_ids
        )
        clean_datasets["order_items"] = clean_items
        self.report.table_metrics["order_items"] = asdict(item_metric)

        # 5. Payments
        clean_payments, pay_metric = self._validate_payments(raw_datasets["payments"], valid_order_ids)
        clean_datasets["payments"] = clean_payments
        self.report.table_metrics["payments"] = asdict(pay_metric)

        # 6. Returns
        clean_returns, ret_metric = self._validate_returns(
            raw_datasets["returns"], valid_order_ids, valid_prod_ids
        )
        clean_datasets["returns"] = clean_returns
        self.report.table_metrics["returns"] = asdict(ret_metric)

        # Compute aggregates
        for metric in self.report.table_metrics.values():
            self.report.total_records_processed += metric["total_raw_rows"]
            self.report.total_duplicates_removed += metric["duplicates_removed"]
            self.report.total_invalid_quarantined += metric["invalid_rows_quarantined"]
            self.report.total_clean_records += metric["clean_rows_retained"]

        self._save_quality_report()
        logger.info("--- Data Quality Audit Finished Successfully ---")
        return clean_datasets, self.report

    def _validate_customers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, TableQualityMetric]:
        metric = TableQualityMetric(table_name="customers", total_raw_rows=len(df))
        df = df.copy()

        # Check missing values
        null_emails = df["email"].isna().sum()
        if null_emails > 0:
            metric.missing_values_detected += int(null_emails)
            metric.anomalies_detected.append(f"Imputed {null_emails} missing customer emails with fallback identifiers.")
            # Impute missing email using customer_id
            df["email"] = df.apply(
                lambda row: f"user_{row['customer_id'].lower()}@retailpulse-guest.com" if pd.isna(row["email"]) else row["email"],
                axis=1,
            )

        # Whitespace normalization
        df["name"] = df["name"].astype(str).str.strip()
        df["email"] = df["email"].astype(str).str.strip().str.lower()

        # Deduplication
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["customer_id"], keep="first")
        dups_removed = before_dedup - len(df)
        metric.duplicates_removed = dups_removed
        if dups_removed > 0:
            metric.anomalies_detected.append(f"Removed {dups_removed} duplicate customer records.")

        # Validate signup dates
        df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
        invalid_dates = df["signup_date"].isna().sum()
        if invalid_dates > 0:
            metric.invalid_rows_quarantined += int(invalid_dates)
            df = df.dropna(subset=["signup_date"])

        metric.clean_rows_retained = len(df)
        return df, metric

    def _validate_products(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, TableQualityMetric]:
        metric = TableQualityMetric(table_name="products", total_raw_rows=len(df))
        df = df.copy()

        # Deduplication
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["product_id"], keep="first")
        dups_removed = before_dedup - len(df)
        metric.duplicates_removed = dups_removed

        # Price and cost validation (must be positive)
        invalid_prices = ((df["price"] <= 0) | (df["cost"] <= 0)).sum()
        if invalid_prices > 0:
            metric.invalid_rows_quarantined += int(invalid_prices)
            metric.anomalies_detected.append(f"Quarantined {invalid_prices} products with non-positive price/cost.")
            df = df[(df["price"] > 0) & (df["cost"] > 0)]

        # String cleanup
        df["product_name"] = df["product_name"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip()
        df["subcategory"] = df["subcategory"].astype(str).str.strip()

        metric.clean_rows_retained = len(df)
        return df, metric

    def _validate_orders(
        self, df: pd.DataFrame, valid_customer_ids: Set[str]
    ) -> Tuple[pd.DataFrame, TableQualityMetric]:
        metric = TableQualityMetric(table_name="orders", total_raw_rows=len(df))
        df = df.copy()

        # Deduplication
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["order_id"], keep="first")
        dups_removed = before_dedup - len(df)
        metric.duplicates_removed = dups_removed

        # Foreign key integrity (customer_id must exist)
        fk_invalid = (~df["customer_id"].isin(valid_customer_ids)).sum()
        if fk_invalid > 0:
            metric.invalid_rows_quarantined += int(fk_invalid)
            metric.anomalies_detected.append(f"Quarantined {fk_invalid} orders referencing invalid customer_ids.")
            df = df[df["customer_id"].isin(valid_customer_ids)]

        # Date validation
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        invalid_dates = df["order_date"].isna().sum()
        if invalid_dates > 0:
            metric.invalid_rows_quarantined += int(invalid_dates)
            df = df.dropna(subset=["order_date"])

        # Numerical fields
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
        df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)
        invalid_totals = (df["total_amount"] < 0).sum()
        if invalid_totals > 0:
            metric.invalid_rows_quarantined += int(invalid_totals)
            df = df[df["total_amount"] >= 0]

        metric.clean_rows_retained = len(df)
        return df, metric

    def _validate_order_items(
        self, df: pd.DataFrame, valid_order_ids: Set[str], valid_product_ids: Set[str]
    ) -> Tuple[pd.DataFrame, TableQualityMetric]:
        metric = TableQualityMetric(table_name="order_items", total_raw_rows=len(df))
        df = df.copy()

        # Deduplication
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["order_item_id"], keep="first")
        dups_removed = before_dedup - len(df)
        metric.duplicates_removed = dups_removed

        # Foreign keys check
        fk_invalid = (~df["order_id"].isin(valid_order_ids) | ~df["product_id"].isin(valid_product_ids)).sum()
        if fk_invalid > 0:
            metric.invalid_rows_quarantined += int(fk_invalid)
            metric.anomalies_detected.append(f"Quarantined {fk_invalid} order items referencing orphan order/product IDs.")
            df = df[df["order_id"].isin(valid_order_ids) & df["product_id"].isin(valid_product_ids)]

        # Numerical check: quantity > 0, unit_price > 0, discount >= 0
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
        df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)

        invalid_numerics = ((df["quantity"] <= 0) | (df["unit_price"] <= 0) | (df["discount"] < 0)).sum()
        if invalid_numerics > 0:
            metric.invalid_rows_quarantined += int(invalid_numerics)
            metric.anomalies_detected.append(f"Quarantined {invalid_numerics} order items with invalid negative/zero values.")
            df = df[(df["quantity"] > 0) & (df["unit_price"] > 0) & (df["discount"] >= 0)]

        metric.clean_rows_retained = len(df)
        return df, metric

    def _validate_payments(
        self, df: pd.DataFrame, valid_order_ids: Set[str]
    ) -> Tuple[pd.DataFrame, TableQualityMetric]:
        metric = TableQualityMetric(table_name="payments", total_raw_rows=len(df))
        df = df.copy()

        df = df.drop_duplicates(subset=["payment_id"], keep="first")
        metric.duplicates_removed = metric.total_raw_rows - len(df)

        df = df[df["order_id"].isin(valid_order_ids)]
        metric.invalid_rows_quarantined = (metric.total_raw_rows - metric.duplicates_removed) - len(df)

        df["payment_amount"] = pd.to_numeric(df["payment_amount"], errors="coerce").fillna(0.0)
        df = df[df["payment_amount"] >= 0]

        metric.clean_rows_retained = len(df)
        return df, metric

    def _validate_returns(
        self, df: pd.DataFrame, valid_order_ids: Set[str], valid_product_ids: Set[str]
    ) -> Tuple[pd.DataFrame, TableQualityMetric]:
        metric = TableQualityMetric(table_name="returns", total_raw_rows=len(df))
        df = df.copy()

        df = df.drop_duplicates(subset=["return_id"], keep="first")
        metric.duplicates_removed = metric.total_raw_rows - len(df)

        df = df[df["order_id"].isin(valid_order_ids) & df["product_id"].isin(valid_product_ids)]
        df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce").fillna(0.0)
        df = df[df["refund_amount"] >= 0]

        metric.invalid_rows_quarantined = (metric.total_raw_rows - metric.duplicates_removed) - len(df)
        metric.clean_rows_retained = len(df)
        return df, metric

    def _save_quality_report(self) -> None:
        report_path = PROCESSED_DATA_DIR / "data_quality_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.report), f, indent=2)
        logger.info(f"Data Quality Report saved to {report_path}")
