-- ==========================================================
-- Product: Bottom 20 Underperforming Products by Revenue
-- Identifies low-velocity inventory items for clearance or rationalization
-- ==========================================================
WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.price,
        COALESCE(SUM(oi.quantity), 0) AS units_sold,
        COALESCE(ROUND(SUM(oi.net_amount), 2), 0.0) AS total_revenue,
        COALESCE(ROUND(SUM(oi.profit), 2), 0.0) AS total_profit
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status IN ('Completed', 'Shipped')
    GROUP BY p.product_id, p.product_name, p.category, p.subcategory, p.price
)
SELECT
    DENSE_RANK() OVER (ORDER BY total_revenue ASC, units_sold ASC) AS underperformance_rank,
    product_id,
    product_name,
    category,
    subcategory,
    price,
    units_sold,
    total_revenue,
    total_profit
FROM product_sales
ORDER BY underperformance_rank ASC
LIMIT 20;
