-- ==========================================================
-- Revenue: Monthly Revenue and Order Trajectory
-- Aggregates orders, distinct customers, and net revenue by month
-- ==========================================================
SELECT
    SUBSTR(order_date, 1, 7) AS sales_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(total_amount), 2) AS monthly_revenue,
    ROUND(AVG(total_amount), 2) AS monthly_aov,
    ROUND(SUM(estimated_profit), 2) AS monthly_profit
FROM orders
WHERE order_status IN ('Completed', 'Shipped')
GROUP BY SUBSTR(order_date, 1, 7)
ORDER BY sales_month ASC;
