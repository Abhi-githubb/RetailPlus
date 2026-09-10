-- ==========================================================
-- Product: Top 20 Best-Selling Products by Revenue
-- Employs DENSE_RANK() to rank highest grossing catalogue items
-- ==========================================================
WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.price,
        p.cost,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.net_amount), 2) AS total_revenue,
        ROUND(SUM(oi.profit), 2) AS total_profit,
        ROUND((SUM(oi.profit) / NULLIF(SUM(oi.net_amount), 0)) * 100.0, 2) AS profit_margin_pct
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY p.product_id, p.product_name, p.category, p.subcategory, p.price, p.cost
)
SELECT
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS sales_rank,
    product_id,
    product_name,
    category,
    subcategory,
    price,
    units_sold,
    total_revenue,
    total_profit,
    profit_margin_pct
FROM product_sales
ORDER BY sales_rank ASC
LIMIT 20;
