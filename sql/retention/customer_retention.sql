-- ==========================================================
-- Retention: Customer Retention and Repeat Purchase Velocity
-- Measures intervals between customer orders and repurchase retention
-- ==========================================================
WITH customer_order_timeline AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS order_number,
        LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS prior_order_date
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
),
customer_summary AS (
    SELECT
        customer_id,
        COUNT(order_id) AS total_orders,
        MIN(order_date) AS first_order,
        MAX(order_date) AS last_order
    FROM customer_order_timeline
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_customers_evaluated,
    COUNT(CASE WHEN total_orders = 1 THEN 1 END) AS single_order_customers,
    COUNT(CASE WHEN total_orders >= 2 THEN 1 END) AS retained_repeat_customers,
    ROUND(COUNT(CASE WHEN total_orders >= 2 THEN 1 END) * 100.0 / COUNT(*), 2) AS overall_retention_rate_pct,
    COUNT(CASE WHEN total_orders >= 4 THEN 1 END) AS loyal_cohort_4plus_orders,
    ROUND(COUNT(CASE WHEN total_orders >= 4 THEN 1 END) * 100.0 / COUNT(*), 2) AS loyalty_retention_rate_pct
FROM customer_summary;
