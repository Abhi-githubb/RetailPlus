"""
Unit tests for RetailPulse Data Quality & Validation Engine.
"""

import pandas as pd
import pytest
from src.validation.data_quality import DataQualityValidator


def test_customer_validation_imputes_missing_and_deduplicates():
    validator = DataQualityValidator()
    raw_customers = pd.DataFrame({
        "customer_id": ["CUST-1", "CUST-2", "CUST-1"],  # CUST-1 duplicated
        "name": [" Alice  ", "Bob", "Alice"],
        "email": [None, "bob@test.com", "alice@test.com"],  # 1 missing email
        "signup_date": ["2023-01-01 10:00:00", "2023-01-02 12:00:00", "2023-01-01 10:00:00"],
        "country": ["United States", "Germany", "United States"],
        "region": ["North America", "Europe", "North America"],
        "acquisition_channel": ["Organic Search", "Direct", "Organic Search"],
    })

    clean_df, metric = validator._validate_customers(raw_customers)

    assert len(clean_df) == 2
    assert metric.duplicates_removed == 1
    assert metric.missing_values_detected == 1
    assert clean_df.loc[clean_df["customer_id"] == "CUST-1", "name"].values[0] == "Alice"
    assert "@" in clean_df.loc[clean_df["customer_id"] == "CUST-1", "email"].values[0]


def test_product_validation_quarantines_negative_prices():
    validator = DataQualityValidator()
    raw_products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Prod 1", "Prod 2", "Prod 3"],
        "category": ["Electronics", "Books", "Apparel"],
        "subcategory": ["Audio", "Fiction", "Shoes"],
        "price": [100.0, -5.0, 50.0],  # P2 has invalid negative price
        "cost": [50.0, 2.0, -10.0],    # P3 has invalid negative cost
        "launch_date": ["2023-01-01", "2023-01-01", "2023-01-01"],
    })

    clean_df, metric = validator._validate_products(raw_products)

    assert len(clean_df) == 1
    assert metric.invalid_rows_quarantined == 2
    assert clean_df.iloc[0]["product_id"] == "P1"


def test_order_items_validation_quarantines_orphan_foreign_keys():
    validator = DataQualityValidator()
    valid_orders = {"ORD-1", "ORD-2"}
    valid_products = {"PROD-1", "PROD-2"}

    raw_items = pd.DataFrame({
        "order_item_id": ["ITEM-1", "ITEM-2", "ITEM-3"],
        "order_id": ["ORD-1", "ORD-UNKNOWN", "ORD-2"],  # ITEM-2 has orphan order_id
        "product_id": ["PROD-1", "PROD-2", "PROD-UNKNOWN"],  # ITEM-3 has orphan product_id
        "quantity": [1, 2, 1],
        "unit_price": [20.0, 30.0, 15.0],
        "discount": [0.0, 0.0, 0.0],
    })

    clean_df, metric = validator._validate_order_items(raw_items, valid_orders, valid_products)

    assert len(clean_df) == 1
    assert clean_df.iloc[0]["order_item_id"] == "ITEM-1"
    assert metric.invalid_rows_quarantined == 2
