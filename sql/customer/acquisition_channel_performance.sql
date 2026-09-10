-- ==========================================================
-- Customer: Acquisition Channel Efficiency & Return
-- Evaluates volume, revenue, average customer spend, and repeat purchase loyalty
-- ==========================================================
WITH customer_orders_summary AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(CASE WHEN o.order_status IN ('Completed', 'Shipped') THEN o.total_amount ELSE 0 END), 0) AS total_revenue
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.acquisition_channel
)
SELECT
    acquisition_channel,
    COUNT(customer_id) AS total_acquired_customers,
    COUNT(CASE WHEN total_orders > 0 THEN customer_id END) AS transacting_customers,
    SUM(total_orders) AS total_orders_generated,
    ROUND(SUM(total_revenue), 2) AS total_revenue_generated,
    ROUND(SUM(total_revenue) / NULLIF(COUNT(customer_id), 0), 2) AS revenue_per_acquired_customer,
    ROUND(SUM(total_revenue) / NULLIF(COUNT(CASE WHEN total_orders > 0 THEN customer_id END), 0), 2) AS average_active_clv,
    ROUND(
        COUNT(CASE WHEN total_orders > 1 THEN customer_id END) * 100.0 /
        NULLIF(COUNT(CASE WHEN total_orders > 0 THEN customer_id END), 0), 2
    ) AS repeat_purchase_rate_pct
FROM customer_orders_summary
GROUP BY acquisition_channel
ORDER BY total_revenue_generated DESC;
