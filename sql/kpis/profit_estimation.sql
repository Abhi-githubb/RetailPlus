-- ==========================================================
-- KPI: Gross & Net Profit Estimation
-- Combines product unit costs, discounts, and order item margins
-- ==========================================================
WITH financials AS (
    SELECT
        ROUND(SUM(oi.net_amount), 2) AS total_revenue,
        ROUND(SUM(oi.total_cost), 2) AS total_cost_of_goods_sold,
        ROUND(SUM(oi.profit), 2) AS total_gross_profit,
        ROUND(SUM(oi.discount), 2) AS total_discounts
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Completed', 'Shipped')
)
SELECT
    total_revenue,
    total_cost_of_goods_sold,
    total_gross_profit,
    total_discounts,
    ROUND((total_gross_profit / NULLIF(total_revenue, 0)) * 100.0, 2) AS gross_profit_margin_pct
FROM financials;
