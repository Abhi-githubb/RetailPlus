-- ==========================================================
-- Revenue: Category Contribution and Pareto Concentration
-- Analyzes sales share, units moved, and profitability by category
-- ==========================================================
WITH category_stats AS (
    SELECT
        p.category,
        COUNT(DISTINCT p.product_id) AS product_catalog_count,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.net_amount), 2) AS category_revenue,
        ROUND(SUM(oi.profit), 2) AS category_profit,
        ROUND(SUM(oi.discount), 2) AS total_discounts_granted
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY p.category
)
SELECT
    category,
    product_catalog_count,
    total_units_sold,
    category_revenue,
    ROUND(category_revenue * 100.0 / SUM(category_revenue) OVER(), 2) AS revenue_contribution_pct,
    category_profit,
    ROUND((category_profit / NULLIF(category_revenue, 0)) * 100.0, 2) AS profit_margin_pct,
    total_discounts_granted
FROM category_stats
ORDER BY category_revenue DESC;
