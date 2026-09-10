-- ==========================================================
-- KPI: Total Orders by Status and Fulfillment Distribution
-- Evaluates fulfillment efficiency and order status breakdown
-- ==========================================================
SELECT
    order_status,
    COUNT(order_id) AS order_count,
    ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER(), 2) AS percentage_share,
    ROUND(SUM(total_amount), 2) AS total_value
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;
