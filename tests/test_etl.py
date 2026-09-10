"""
Unit tests for RetailPulse Data Transformations & Feature Engineering.
"""

import pandas as pd
from src.transformation.cleaner import DataTransformer


def test_data_transformer_computes_margins_and_profits():
    transformer = DataTransformer()

    customers = pd.DataFrame({
        "customer_id": ["CUST-1"],
        "name": ["Alice"],
        "email": ["alice@test.com"],
        "signup_date": ["2023-01-01 10:00:00"],
        "country": ["United States"],
        "region": ["North America"],
        "acquisition_channel": ["Organic Search"],
    })
    products = pd.DataFrame({
        "product_id": ["PROD-1"],
        "product_name": ["Wireless Headphones"],
        "category": ["Electronics"],
        "subcategory": ["Audio"],
        "price": [100.0],
        "cost": [60.0],
        "launch_date": ["2023-01-01"],
    })
    orders = pd.DataFrame({
        "order_id": ["ORD-1"],
        "customer_id": ["CUST-1"],
        "order_date": ["2023-02-01 14:00:00"],
        "order_status": ["Completed"],
        "shipping_region": ["North America"],
        "payment_method": ["Credit Card"],
        "discount": [10.0],
        "total_amount": [90.0],
    })
    order_items = pd.DataFrame({
        "order_item_id": ["ITEM-1"],
        "order_id": ["ORD-1"],
        "product_id": ["PROD-1"],
        "quantity": [1],
        "unit_price": [100.0],
        "discount": [10.0],
    })
    payments = pd.DataFrame({
        "payment_id": ["PAY-1"],
        "order_id": ["ORD-1"],
        "payment_date": ["2023-02-01 14:05:00"],
        "payment_method": ["Credit Card"],
        "payment_status": ["Success"],
        "payment_amount": [90.0],
    })
    returns = pd.DataFrame(columns=["return_id", "order_id", "product_id", "return_date", "return_reason", "refund_amount"])

    clean_data = {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "returns": returns,
    }

    result = transformer.transform_all(clean_data)

    items_res = result["order_items"]
    assert items_res.iloc[0]["gross_amount"] == 100.0
    assert items_res.iloc[0]["net_amount"] == 90.0
    assert items_res.iloc[0]["total_cost"] == 60.0
    assert items_res.iloc[0]["profit"] == 30.0  # 90 net - 60 cost

    orders_res = result["orders"]
    assert orders_res.iloc[0]["total_items"] == 1
    assert orders_res.iloc[0]["estimated_profit"] == 30.0
