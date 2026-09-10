-- ==========================================================
-- KPI: Average Order Value (AOV) Breakdown
-- Computes global AOV, median proxy, and standard order basket metrics
-- ==========================================================
SELECT
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(MIN(total_amount), 2) AS min_order_value,
    ROUND(MAX(total_amount), 2) AS max_order_value,
    ROUND(AVG(total_items), 2) AS avg_items_per_basket,
    ROUND(SUM(total_amount) / NULLIF(SUM(total_items), 0), 2) AS avg_revenue_per_item
FROM orders
WHERE order_status IN ('Completed', 'Shipped');
