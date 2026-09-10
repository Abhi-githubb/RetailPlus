-- ==========================================================
-- RetailPulse Analytical Views / Materialized SQL Layer
-- ==========================================================

-- 1. Daily Sales Performance
DROP VIEW IF EXISTS daily_sales;
CREATE VIEW daily_sales AS
SELECT
    SUBSTR(order_date, 1, 10) AS sales_date,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(total_amount), 2) AS gross_revenue,
    ROUND(SUM(discount), 2) AS total_discount,
    ROUND(SUM(total_amount), 2) AS net_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(estimated_profit), 2) AS total_profit
FROM orders
WHERE order_status IN ('Completed', 'Shipped')
GROUP BY SUBSTR(order_date, 1, 10);

-- 2. Monthly Sales & Growth
DROP VIEW IF EXISTS monthly_sales;
CREATE VIEW monthly_sales AS
SELECT
    SUBSTR(order_date, 1, 7) AS sales_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(estimated_profit), 2) AS total_profit
FROM orders
WHERE order_status IN ('Completed', 'Shipped')
GROUP BY SUBSTR(order_date, 1, 7);

-- 3. Customer RFM & Lifetime Metrics
DROP VIEW IF EXISTS customer_metrics;
CREATE VIEW customer_metrics AS
SELECT
    c.customer_id,
    c.name,
    c.email,
    c.country,
    c.region,
    c.acquisition_channel,
    c.signup_date,
    COUNT(o.order_id) AS lifetime_orders,
    COALESCE(ROUND(SUM(CASE WHEN o.order_status IN ('Completed', 'Shipped') THEN o.total_amount ELSE 0 END), 2), 0.0) AS lifetime_spend,
    COALESCE(ROUND(AVG(CASE WHEN o.order_status IN ('Completed', 'Shipped') THEN o.total_amount ELSE NULL END), 2), 0.0) AS average_order_value,
    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.country, c.region, c.acquisition_channel, c.signup_date;

-- 4. Product Performance Metrics
DROP VIEW IF EXISTS product_performance;
CREATE VIEW product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.price,
    p.cost,
    ROUND(p.price - p.cost, 2) AS unit_margin,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(ROUND(SUM(oi.net_amount), 2), 0.0) AS total_revenue,
    COALESCE(ROUND(SUM(oi.profit), 2), 0.0) AS total_profit,
    COUNT(DISTINCT r.return_id) AS total_returns
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN returns r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name, p.category, p.subcategory, p.price, p.cost;

-- 5. Category Performance Summary
DROP VIEW IF EXISTS category_performance;
CREATE VIEW category_performance AS
SELECT
    p.category,
    COUNT(DISTINCT p.product_id) AS total_products,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(ROUND(SUM(oi.net_amount), 2), 0.0) AS total_revenue,
    COALESCE(ROUND(SUM(oi.profit), 2), 0.0) AS total_profit,
    COUNT(DISTINCT r.return_id) AS return_count,
    ROUND(
        CASE
            WHEN SUM(oi.quantity) > 0 THEN (COUNT(DISTINCT r.return_id) * 1.0 / SUM(oi.quantity)) * 100
            ELSE 0.0
        END, 2
    ) AS return_rate_percent
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN returns r ON p.product_id = r.product_id
GROUP BY p.category;

-- 6. Regional Performance Breakdown
DROP VIEW IF EXISTS regional_performance;
CREATE VIEW regional_performance AS
SELECT
    o.shipping_region AS region,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS average_order_value,
    ROUND(SUM(o.estimated_profit), 2) AS total_profit
FROM orders o
WHERE o.order_status IN ('Completed', 'Shipped')
GROUP BY o.shipping_region;

-- 7. Retention Metrics
DROP VIEW IF EXISTS retention_metrics;
CREATE VIEW retention_metrics AS
SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) AS total_acquired,
    COUNT(DISTINCT CASE WHEN cm.lifetime_orders > 1 THEN c.customer_id END) AS repeat_customers,
    ROUND(
        (COUNT(DISTINCT CASE WHEN cm.lifetime_orders > 1 THEN c.customer_id END) * 100.0) /
        NULLIF(COUNT(DISTINCT c.customer_id), 0),
        2
    ) AS repeat_purchase_rate_pct,
    ROUND(AVG(cm.lifetime_spend), 2) AS avg_clv
FROM customers c
JOIN customer_metrics cm ON c.customer_id = cm.customer_id
GROUP BY c.acquisition_channel;

-- 8. Return Metrics Overview
DROP VIEW IF EXISTS return_metrics;
CREATE VIEW return_metrics AS
SELECT
    r.return_reason,
    COUNT(r.return_id) AS return_count,
    ROUND(SUM(r.refund_amount), 2) AS total_refunded,
    ROUND(AVG(r.refund_amount), 2) AS avg_refund_amount
FROM returns r
GROUP BY r.return_reason;

-- 9. Cohort Monthly Matrix Base View
DROP VIEW IF EXISTS cohort_analysis;
CREATE VIEW cohort_analysis AS
WITH customer_cohorts AS (
    SELECT
        customer_id,
        SUBSTR(MIN(order_date), 1, 7) AS cohort_month
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY customer_id
),
customer_orders AS (
    SELECT
        o.customer_id,
        cc.cohort_month,
        SUBSTR(o.order_date, 1, 7) AS order_month
    FROM orders o
    JOIN customer_cohorts cc ON o.customer_id = cc.customer_id
    WHERE o.order_status IN ('Completed', 'Shipped')
)
SELECT
    cohort_month,
    order_month,
    COUNT(DISTINCT customer_id) AS active_customers
FROM customer_orders
GROUP BY cohort_month, order_month;
