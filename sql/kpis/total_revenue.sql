-- ==========================================================
-- KPI: Total Gross & Net Revenue
-- Calculates completed/shipped revenue and discount deductions
-- ==========================================================
SELECT
    COUNT(order_id) AS total_valid_orders,
    ROUND(SUM(total_amount), 2) AS total_net_revenue,
    ROUND(SUM(discount), 2) AS total_discounts_applied,
    ROUND(SUM(total_amount + discount), 2) AS total_gross_revenue,
    ROUND(AVG(total_amount), 2) AS overall_aov
FROM orders
WHERE order_status IN ('Completed', 'Shipped');
