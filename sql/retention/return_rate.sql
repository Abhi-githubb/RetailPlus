-- ==========================================================
-- Retention: Return Rate & Lost Revenue Analysis
-- Computes return frequency, refund loss, and worst-performing categories by return %
-- ==========================================================
WITH category_return_stats AS (
    SELECT
        p.category,
        COUNT(DISTINCT oi.order_item_id) AS total_items_sold,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.net_amount), 2) AS total_category_revenue,
        COUNT(DISTINCT r.return_id) AS total_returns_filed,
        ROUND(COALESCE(SUM(r.refund_amount), 0.0), 2) AS total_refunded_amount
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN returns r ON oi.order_id = r.order_id AND oi.product_id = r.product_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY p.category
)
SELECT
    category,
    total_units_sold,
    total_category_revenue,
    total_returns_filed,
    ROUND((total_returns_filed * 100.0 / NULLIF(total_units_sold, 0)), 2) AS return_rate_pct,
    total_refunded_amount,
    ROUND((total_refunded_amount * 100.0 / NULLIF(total_category_revenue, 0)), 2) AS refund_value_loss_pct
FROM category_return_stats
ORDER BY return_rate_pct DESC;
