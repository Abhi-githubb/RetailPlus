"""
FastAPI Route Controllers for RetailPulse.
Exposes high-performance analytical endpoints backed by parameterized SQL queries.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.database.connection import check_db_connection
from src.analytics.query_runner import query_runner
from src.utils.config import PROCESSED_DATA_DIR
from app.api.schemas import (
    HealthResponse,
    SummaryMetricsResponse,
    SalesTrendItem,
    CategoryMetricItem,
    RegionalMetricItem,
    ProductItem,
    CustomerMetricItem,
    RetentionSummaryResponse,
    CohortItem,
    OrderItemDetail,
    DataQualitySummaryResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System Health"])
def health_check():
    """System health and database connectivity probe."""
    db_ok, db_info = check_db_connection()
    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database_connected=db_ok,
        database_info=db_info,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@router.get("/api/summary", response_model=SummaryMetricsResponse, tags=["Executive Analytics"])
def get_executive_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Geographic region"),
    category: Optional[str] = Query(None, description="Product category"),
):
    """Returns top-level business KPIs (Revenue, Orders, AOV, Profit, Margin, Returns)."""
    try:
        data = query_runner.get_kpi_summary(
            start_date=start_date,
            end_date=end_date,
            region=region,
            category=category,
        )
        return SummaryMetricsResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate summary metrics: {str(e)}")


@router.get("/api/sales", response_model=List[SalesTrendItem], tags=["Sales Analytics"])
def get_sales_trends(
    granularity: str = Query("monthly", pattern="^(daily|monthly)$", description="Aggregation level"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Geographic region"),
    category: Optional[str] = Query(None, description="Product category"),
):
    """Returns time-series revenue and order volume trends."""
    try:
        df = query_runner.get_sales_trend(
            granularity=granularity,
            start_date=start_date,
            end_date=end_date,
            region=region,
            category=category,
        )
        period_col = "sales_month" if granularity == "monthly" else "sales_date"
        results = []
        for _, row in df.iterrows():
            results.append(
                SalesTrendItem(
                    period=str(row[period_col]),
                    total_orders=int(row["total_orders"]),
                    active_customers=int(row["active_customers"]),
                    total_revenue=float(row["total_revenue"]),
                    average_order_value=float(row["average_order_value"]),
                    total_profit=float(row["total_profit"]),
                )
            )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales trends: {str(e)}")


@router.get("/api/categories", response_model=List[CategoryMetricItem], tags=["Product Analytics"])
def get_categories_performance(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Geographic region"),
):
    """Returns category revenue, unit volumes, and margins."""
    try:
        df = query_runner.get_category_breakdown(
            start_date=start_date,
            end_date=end_date,
            region=region,
        )
        results = []
        for _, row in df.iterrows():
            results.append(
                CategoryMetricItem(
                    category=str(row["category"]),
                    units_sold=int(row["units_sold"]),
                    category_revenue=float(row["category_revenue"]),
                    category_profit=float(row["category_profit"]),
                    margin_pct=float(row["margin_pct"]),
                )
            )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories performance: {str(e)}")


@router.get("/api/products", response_model=List[ProductItem], tags=["Product Analytics"])
def get_products_performance(
    limit: int = Query(20, ge=1, le=100, description="Max products to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ascending: bool = Query(False, description="Order ascending (bottom products) or descending (top products)"),
):
    """Returns top or bottom products ranked by total revenue."""
    try:
        df = query_runner.get_top_products_table(
            limit=limit,
            category=category,
            ascending=ascending,
        )
        results = []
        for _, row in df.iterrows():
            results.append(
                ProductItem(
                    product_id=str(row["product_id"]),
                    product_name=str(row["product_name"]),
                    category=str(row["category"]),
                    subcategory=str(row["subcategory"]),
                    price=float(row["price"]),
                    units_sold=int(row["units_sold"]),
                    total_revenue=float(row["total_revenue"]),
                    total_profit=float(row["total_profit"]),
                    margin_pct=float(row["margin_pct"]),
                )
            )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products performance: {str(e)}")


@router.get("/api/regions", response_model=List[RegionalMetricItem], tags=["Regional Analytics"])
def get_regional_performance(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Product category"),
):
    """Returns geographic revenue, order volume, and AOV by region."""
    try:
        df = query_runner.get_regional_breakdown(
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
        results = []
        for _, row in df.iterrows():
            results.append(
                RegionalMetricItem(
                    region=str(row["region"]),
                    total_orders=int(row["total_orders"]),
                    unique_customers=int(row["unique_customers"]),
                    total_revenue=float(row["total_revenue"]),
                    average_order_value=float(row["average_order_value"]),
                    total_profit=float(row["total_profit"]),
                )
            )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch regional breakdown: {str(e)}")


@router.get("/api/customers", response_model=List[CustomerMetricItem], tags=["Customer Analytics"])
def get_customers(
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    region: Optional[str] = Query(None, description="Geographic region"),
    channel: Optional[str] = Query(None, description="Acquisition channel"),
):
    """Returns customer profiles with lifetime spend and order frequency."""
    try:
        where = []
        params = {"limit": limit}
        if region and region != "All":
            where.append("region = :region")
            params["region"] = region
        if channel and channel != "All":
            where.append("acquisition_channel = :channel")
            params["channel"] = channel

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        query = f"""
        SELECT customer_id, name, email, country, region, acquisition_channel,
               lifetime_orders, lifetime_spend, average_order_value
        FROM customer_metrics
        {where_sql}
        ORDER BY lifetime_spend DESC
        LIMIT :limit;
        """
        df = query_runner.execute_raw_sql(query, params)
        results = []
        for _, row in df.iterrows():
            results.append(CustomerMetricItem(**row.to_dict()))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")


@router.get("/api/retention", response_model=RetentionSummaryResponse, tags=["Retention & Cohorts"])
def get_retention_overview():
    """Returns customer repurchase velocity and retention percentages."""
    try:
        df = query_runner.execute_sql_file("retention/customer_retention.sql")
        row = df.iloc[0].to_dict()
        return RetentionSummaryResponse(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch retention metrics: {str(e)}")


@router.get("/api/cohorts", response_model=List[CohortItem], tags=["Retention & Cohorts"])
def get_cohort_retention():
    """Returns monthly cohort retention matrix dataset."""
    try:
        df = query_runner.get_cohort_matrix()
        results = []
        for _, row in df.iterrows():
            results.append(
                CohortItem(
                    cohort_month=str(row["cohort_month"]),
                    cohort_size=int(row["cohort_size"]),
                    month_offset=int(row["month_offset"]),
                    active_retained_customers=int(row["active_retained_customers"]),
                    retention_rate_pct=float(row["retention_rate_pct"]),
                )
            )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cohort matrix: {str(e)}")


@router.get("/api/orders", response_model=List[OrderItemDetail], tags=["Order Transactions"])
def get_orders(
    limit: int = Query(50, ge=1, le=200, description="Max orders to return"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    region: Optional[str] = Query(None, description="Filter by shipping region"),
):
    """Returns recent order transactions."""
    try:
        where = []
        params = {"limit": limit}
        if status and status != "All":
            where.append("order_status = :status")
            params["status"] = status
        if region and region != "All":
            where.append("shipping_region = :region")
            params["region"] = region

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        query = f"""
        SELECT order_id, customer_id, order_date, order_status, shipping_region,
               payment_method, discount, total_amount, total_items, estimated_profit
        FROM orders
        {where_sql}
        ORDER BY order_date DESC
        LIMIT :limit;
        """
        df = query_runner.execute_raw_sql(query, params)
        results = []
        for _, row in df.iterrows():
            results.append(OrderItemDetail(**row.to_dict()))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/api/quality", response_model=DataQualitySummaryResponse, tags=["System Health"])
def get_data_quality_report():
    """Returns the latest data quality, schema validation, and quarantine audit report."""
    report_file = PROCESSED_DATA_DIR / "data_quality_report.json"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Data quality report not found. Run ETL pipeline first.")
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return DataQualitySummaryResponse(**data)
