# RetailPulse — Architecture & Data Engineering Blueprint

This document details the end-to-end technical architecture, data pipeline mechanics, relational database schema, SQL analytics engine, and deployment topologies of **RetailPulse**.

---

## 1. System Architecture Overview

```mermaid
graph TD
    subgraph Data Generation & Raw Ingestion
        A[Synthetic Transaction Generator<br/>NumPy / Pandas Simulation] -->|Raw CSVs| B[Raw Staging Layer<br/>data/raw/]
    end

    subgraph Data Quality & Governance
        B --> C[DataQualityValidator<br/>Schema & Integrity Engine]
        C -->|Audited Anomalies| D[Quarantine & Quality Log<br/>data/processed/data_quality_report.json]
        C -->|Clean DataFrames| E[DataTransformer<br/>Feature & Metric Engineering]
    end

    subgraph Analytical Data Warehouse
        E --> F[DatabaseLoader<br/>Batch Ingestion]
        F --> G[(PostgreSQL / SQLite<br/>Relational Warehouse)]
        G --> H[Analytical Views / Aggregations<br/>daily_sales, monthly_sales, cohorts]
    end

    subgraph Application & Delivery Layer
        G --> I[SQL Analytics Library<br/>22+ Modular CTE / Window Queries]
        I --> J[FastAPI REST API<br/>Pydantic Contracts & OpenAPI]
        I --> K[Streamlit SaaS Dashboard<br/>Plotly Interactive Visuals & Dynamic Insights]
        J -.-> K
    end
```

---

## 2. Relational Schema & Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    customers ||--o{ orders : places
    products ||--o{ order_items : contains
    orders ||--|{ order_items : includes
    orders ||--o{ payments : completes
    orders ||--o{ returns : generates
    products ||--o{ returns : references

    customers {
        varchar(32) customer_id PK
        varchar(128) name
        varchar(128) email
        timestamp signup_date
        varchar(64) country
        varchar(64) region
        varchar(64) acquisition_channel
    }

    products {
        varchar(32) product_id PK
        varchar(255) product_name
        varchar(64) category
        varchar(64) subcategory
        numeric price
        numeric cost
        date launch_date
    }

    orders {
        varchar(32) order_id PK
        varchar(32) customer_id FK
        timestamp order_date
        varchar(32) order_status
        varchar(64) shipping_region
        varchar(64) payment_method
        numeric discount
        numeric total_amount
        integer total_items
        integer unique_products
        numeric estimated_profit
    }

    order_items {
        varchar(32) order_item_id PK
        varchar(32) order_id FK
        varchar(32) product_id FK
        integer quantity
        numeric unit_price
        numeric discount
        numeric product_cost
        numeric gross_amount
        numeric net_amount
        numeric total_cost
        numeric profit
    }

    payments {
        varchar(32) payment_id PK
        varchar(32) order_id FK
        timestamp payment_date
        varchar(64) payment_method
        varchar(32) payment_status
        numeric payment_amount
    }

    returns {
        varchar(32) return_id PK
        varchar(32) order_id FK
        varchar(32) product_id FK
        timestamp return_date
        varchar(128) return_reason
        numeric refund_amount
    }
```

---

## 3. Data Pipeline & ETL Workflow

### Step 1: Ingestion & Realistic Simulation
- Generates 105,000+ orders, 22,000+ customers, 550+ products over 2.5 years.
- Incorporates realistic e-commerce mechanics:
  - **Pareto Spend Distribution**: 20% of customers drive 70% of repeat transactions.
  - **Holiday & Promo Seasonality**: Q4 spikes (Black Friday, Cyber Week) and mid-year sales surges.
  - **Category-Calibrated Returns**: Higher return rates in Apparel (~16%) versus Electronics (~7%) and Books (~2%).
  - **Controlled Dirty Data**: Injected edge cases (whitespace, duplicate IDs, missing emails, invalid prices) to stress-test data validation.

### Step 2: Data Quality & Governance Audit
- **Completeness**: Imputes or isolates missing critical fields.
- **Uniqueness**: Deduplicates records using primary keys with deterministic keep logic.
- **Relational Integrity**: Enforces referential integrity (prevents orphan order items and payments).
- **Domain Validity**: Quarantines negative prices, quantities, and invalid date anomalies.
- **Audit Logging**: Emits `data_quality_report.json` with execution counts.

### Step 3: Feature Engineering & Derived Financials
- Calculates line-item gross revenue, discount deductions, net revenue, total cost of goods sold (COGS), and net profit.
- Aggregates order-level item counts, basket size, and estimated profit.

### Step 4 & 5: Relational Warehouse Loading
- High-performance chunked batch loading into PostgreSQL / SQLite.
- Fully idempotent: drops and rebuilds schemas cleanly.

### Step 6: Analytical Views Compilation
- Pre-aggregates daily sales, monthly sales, customer lifetime metrics, product margins, regional penetration, and cohort retention.

---

## 4. SQL Analytics & Metric Framework

The `sql/` directory contains 22 specialized, production-ready SQL scripts organized into 6 domains:

1. **`sql/kpis/`**:
   - `total_revenue.sql`: Net revenue, discounts, gross volume, global AOV.
   - `average_order_value.sql`: Basket size, unit economics, price distribution.
   - `total_orders.sql`: Fulfillment efficiency and order status breakdown.
   - `unique_customers.sql`: Active penetration, repeat buyer share.
   - `profit_estimation.sql`: COGS, gross margins, promotional cost.
2. **`sql/revenue/`**:
   - `monthly_revenue.sql`: Monthly trajectory and active customers.
   - `monthly_growth_rate.sql`: Month-over-Month (MoM) growth using `LAG()`.
   - `yoy_growth.sql`: Year-over-Year comparison across consecutive years.
   - `best_performing_months.sql`: Ranked peak months using `DENSE_RANK()`.
   - `revenue_by_region.sql`: Regional revenue contribution and AOV.
   - `revenue_contribution_by_category.sql`: Category Pareto analysis.
   - `discount_impact.sql`: Discount tiers and margin elasticity.
3. **`sql/customer/`**:
   - `new_vs_returning_customers.sql`: First-time vs repeat classification using `ROW_NUMBER()`.
   - `acquisition_channel_performance.sql`: CAC proxy, average CLV, repeat rate by acquisition source.
   - `customer_lifetime_value.sql`: Value tier segmentation (VIP, High, Mid, Standard).
   - `repeat_purchase_rate.sql`: Order frequency distribution buckets.
   - `customer_segmentation_rfm.sql`: Recency, Frequency, Monetary segmentation using `NTILE(4)`.
4. **`sql/product/`**:
   - `top_products.sql`: Top 20 best-selling SKUs by gross revenue.
   - `bottom_products.sql`: Bottom 20 underperforming inventory SKUs for clearance.
   - `top_categories.sql`: Category and subcategory drilldown with margin metrics.
5. **`sql/retention/`**:
   - `customer_retention.sql`: Repurchase velocity and retention ratios.
   - `return_rate.sql`: Return rate and refund value loss by product category.
6. **`sql/cohorts/`**:
   - `cohort_retention_matrix.sql`: Triangular cohort retention matrix spanning Month 0 to Month 12+.
