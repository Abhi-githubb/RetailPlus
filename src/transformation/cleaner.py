"""
Data Transformation and Feature Engineering Pipeline for RetailPulse.
Transforms cleaned raw entities into analytical-ready datasets, calculates derived
financial and behavioral metrics, and stages them for database ingestion.
"""

from typing import Dict
import numpy as np
import pandas as pd
from src.utils.logger import logger
from src.utils.config import PROCESSED_DATA_DIR


class DataTransformer:
    """Computes derived metrics, normalizes formats, and prepares tables for database ingestion."""

    def transform_all(self, clean_datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Runs transformation and metric derivation across all tables."""
        logger.info("--- Starting Analytical Data Transformations ---")

        customers = clean_datasets["customers"].copy()
        products = clean_datasets["products"].copy()
        orders = clean_datasets["orders"].copy()
        order_items = clean_datasets["order_items"].copy()
        payments = clean_datasets["payments"].copy()
        returns = clean_datasets["returns"].copy()

        # 1. Format dates to standard ISO strings
        customers["signup_date"] = pd.to_datetime(customers["signup_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        products["launch_date"] = pd.to_datetime(products["launch_date"]).dt.strftime("%Y-%m-%d")
        orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        payments["payment_date"] = pd.to_datetime(payments["payment_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        returns["return_date"] = pd.to_datetime(returns["return_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # 2. Enrich order_items with product cost & derived profit
        logger.info("Computing line-item gross revenue, discount, net revenue, and estimated cost...")
        prod_cost_map = dict(zip(products["product_id"], products["cost"]))
        order_items["product_cost"] = order_items["product_id"].map(prod_cost_map).fillna(0.0)
        order_items["gross_amount"] = (order_items["quantity"] * order_items["unit_price"]).round(2)
        order_items["net_amount"] = (order_items["gross_amount"] - order_items["discount"]).round(2)
        order_items["total_cost"] = (order_items["quantity"] * order_items["product_cost"]).round(2)
        order_items["profit"] = (order_items["net_amount"] - order_items["total_cost"]).round(2)

        # 3. Add order-level item aggregations
        logger.info("Aggregating order-level line counts and gross amounts...")
        order_agg = order_items.groupby("order_id").agg(
            total_items=("quantity", "sum"),
            unique_products=("product_id", "nunique"),
            computed_gross=("gross_amount", "sum"),
            computed_discount=("discount", "sum"),
            computed_net=("net_amount", "sum"),
            computed_cost=("total_cost", "sum"),
            computed_profit=("profit", "sum"),
        ).reset_index()

        orders = orders.merge(order_agg, on="order_id", how="left")
        orders["total_items"] = orders["total_items"].fillna(1).astype(int)
        orders["unique_products"] = orders["unique_products"].fillna(1).astype(int)
        orders["estimated_profit"] = orders["computed_profit"].fillna(orders["total_amount"] * 0.45).round(2)
        orders.drop(columns=["computed_gross", "computed_discount", "computed_net", "computed_cost", "computed_profit"], inplace=True)

        # 4. Save processed CSVs
        for table_name, df in [
            ("customers", customers),
            ("products", products),
            ("orders", orders),
            ("order_items", order_items),
            ("payments", payments),
            ("returns", returns),
        ]:
            out_file = PROCESSED_DATA_DIR / f"{table_name}_processed.csv"
            df.to_csv(out_file, index=False)
            logger.info(f"Saved processed dataset: {out_file.name} ({len(df):,} rows)")

        logger.info("--- Data Transformations Completed Successfully ---")
        return {
            "customers": customers,
            "products": products,
            "orders": orders,
            "order_items": order_items,
            "payments": payments,
            "returns": returns,
        }
