-- ==========================================================
-- KPI: Unique Customers Count & Activity Penetration
-- Measures total acquired vs transacting customer base
-- ==========================================================
WITH customer_order_stats AS (
    SELECT
        c.customer_id,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(CASE WHEN o.order_status IN ('Completed', 'Shipped') THEN o.total_amount ELSE 0 END), 0) AS total_spend
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
)
SELECT
    COUNT(*) AS total_registered_customers,
    COUNT(CASE WHEN total_orders > 0 THEN 1 END) AS active_transacting_customers,
    COUNT(CASE WHEN total_orders = 1 THEN 1 END) AS one_time_buyers,
    COUNT(CASE WHEN total_orders > 1 THEN 1 END) AS repeat_buyers,
    ROUND(COUNT(CASE WHEN total_orders > 1 THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN total_orders > 0 THEN 1 END), 0), 2) AS repeat_customer_percentage
FROM customer_order_stats;
