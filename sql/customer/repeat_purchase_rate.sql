-- ==========================================================
-- Customer: Repeat Purchase Frequency Distribution
-- Analyzes order frequency buckets (1 order, 2 orders, 3-5 orders, 6+ orders)
-- ==========================================================
WITH customer_order_frequencies AS (
    SELECT
        customer_id,
        COUNT(order_id) AS order_count,
        ROUND(SUM(total_amount), 2) AS total_spend
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY customer_id
),
frequency_buckets AS (
    SELECT
        customer_id,
        order_count,
        total_spend,
        CASE
            WHEN order_count = 1 THEN '1 Order (One-Time)'
            WHEN order_count = 2 THEN '2 Orders (First Repeat)'
            WHEN order_count BETWEEN 3 AND 5 THEN '3 - 5 Orders (Loyal)'
            ELSE '6+ Orders (Power User)'
        END AS frequency_tier
    FROM customer_order_frequencies
)
SELECT
    frequency_tier,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(), 2) AS pct_of_customers,
    ROUND(SUM(total_spend), 2) AS total_revenue,
    ROUND(SUM(total_spend) * 100.0 / SUM(SUM(total_spend)) OVER(), 2) AS pct_of_revenue,
    ROUND(AVG(total_spend), 2) AS avg_spend_per_customer
FROM frequency_buckets
GROUP BY frequency_tier
ORDER BY total_revenue DESC;
