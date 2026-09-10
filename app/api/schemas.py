"""
Pydantic v2 Schema Definitions for RetailPulse REST API.
Defines strict response models, data contracts, and query parameters.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    database_connected: bool = Field(..., examples=[True])
    database_info: str = Field(..., examples=["Connected successfully (SQLite)"])
    timestamp: str = Field(..., examples=["2025-06-30T12:00:00"])
    version: str = Field(default="1.0.0")


class SummaryMetricsResponse(BaseModel):
    total_orders: int = Field(..., examples=[104950])
    active_customers: int = Field(..., examples=[21500])
    total_revenue: float = Field(..., examples=[25482310.50])
    average_order_value: float = Field(..., examples=[242.80])
    estimated_profit: float = Field(..., examples=[11467039.72])
    profit_margin_pct: float = Field(..., examples=[45.0])
    total_units_sold: int = Field(..., examples=[170420])
    total_returns: int = Field(..., examples=[8420])
    return_rate_pct: float = Field(..., examples=[4.94])
    total_refunded: float = Field(..., examples=[1254300.0])


class SalesTrendItem(BaseModel):
    period: str = Field(..., examples=["2024-01"])
    total_orders: int = Field(..., examples=[4500])
    active_customers: int = Field(..., examples=[3900])
    total_revenue: float = Field(..., examples=[1092300.0])
    average_order_value: float = Field(..., examples=[242.73])
    total_profit: float = Field(..., examples=[491535.0])


class CategoryMetricItem(BaseModel):
    category: str = Field(..., examples=["Electronics"])
    units_sold: int = Field(..., examples=[45000])
    category_revenue: float = Field(..., examples=[8500000.0])
    category_profit: float = Field(..., examples=[3825000.0])
    margin_pct: float = Field(..., examples=[45.0])


class RegionalMetricItem(BaseModel):
    region: str = Field(..., examples=["North America"])
    total_orders: int = Field(..., examples=[44000])
    unique_customers: int = Field(..., examples=[9000])
    total_revenue: float = Field(..., examples=[10702500.0])
    average_order_value: float = Field(..., examples=[243.2])
    total_profit: float = Field(..., examples=[4816125.0])


class ProductItem(BaseModel):
    product_id: str = Field(..., examples=["PROD-1001"])
    product_name: str = Field(..., examples=["Ultra Smartphone Max"])
    category: str = Field(..., examples=["Electronics"])
    subcategory: str = Field(..., examples=["Smartphones"])
    price: float = Field(..., examples=[899.99])
    units_sold: int = Field(..., examples=[1200])
    total_revenue: float = Field(..., examples=[1079988.0])
    total_profit: float = Field(..., examples=[377995.8])
    margin_pct: float = Field(..., examples=[35.0])


class CustomerMetricItem(BaseModel):
    customer_id: str = Field(..., examples=["CUST-10001"])
    name: str = Field(..., examples=["Sarah Connor"])
    email: str = Field(..., examples=["sarah.connor@workmail.com"])
    country: str = Field(..., examples=["United States"])
    region: str = Field(..., examples=["North America"])
    acquisition_channel: str = Field(..., examples=["Organic Search"])
    lifetime_orders: int = Field(..., examples=[5])
    lifetime_spend: float = Field(..., examples=[1420.50])
    average_order_value: float = Field(..., examples=[284.10])


class RetentionSummaryResponse(BaseModel):
    total_customers_evaluated: int = Field(..., examples=[22000])
    single_order_customers: int = Field(..., examples=[12500])
    retained_repeat_customers: int = Field(..., examples=[9500])
    overall_retention_rate_pct: float = Field(..., examples=[43.18])
    loyal_cohort_4plus_orders: int = Field(..., examples=[3100])
    loyalty_retention_rate_pct: float = Field(..., examples=[14.09])


class CohortItem(BaseModel):
    cohort_month: str = Field(..., examples=["2023-01"])
    cohort_size: int = Field(..., examples=[1800])
    month_offset: int = Field(..., examples=[1])
    active_retained_customers: int = Field(..., examples=[450])
    retention_rate_pct: float = Field(..., examples=[25.0])


class OrderItemDetail(BaseModel):
    order_id: str = Field(..., examples=["ORD-1000001"])
    customer_id: str = Field(..., examples=["CUST-100001"])
    order_date: str = Field(..., examples=["2024-03-15 14:22:10"])
    order_status: str = Field(..., examples=["Completed"])
    shipping_region: str = Field(..., examples=["North America"])
    payment_method: str = Field(..., examples=["Credit Card"])
    discount: float = Field(..., examples=[15.0])
    total_amount: float = Field(..., examples=[245.50])
    total_items: int = Field(..., examples=[2])
    estimated_profit: float = Field(..., examples=[110.48])


class DataQualitySummaryResponse(BaseModel):
    execution_timestamp: str
    total_records_processed: int
    total_duplicates_removed: int
    total_invalid_quarantined: int
    total_clean_records: int
    passed_validation: bool
    table_metrics: Dict[str, Any]
