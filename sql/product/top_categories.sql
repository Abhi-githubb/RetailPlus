-- ==========================================================
-- Product: Top Categories and Subcategory Drilldown
-- Aggregates volume, net revenue, average item basket price, and category margin
-- ==========================================================
SELECT
    p.category,
    p.subcategory,
    COUNT(DISTINCT p.product_id) AS active_skus,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.net_amount), 2) AS subcategory_revenue,
    ROUND(SUM(oi.profit), 2) AS subcategory_profit,
    ROUND(AVG(oi.unit_price), 2) AS avg_unit_price,
    ROUND((SUM(oi.profit) / NULLIF(SUM(oi.net_amount), 0)) * 100.0, 2) AS profit_margin_pct
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status IN ('Completed', 'Shipped')
GROUP BY p.category, p.subcategory
ORDER BY subcategory_revenue DESC;
