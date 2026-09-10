-- ==========================================================
-- Revenue: Regional Revenue and Customer Penetration
-- Evaluates market size, average basket, and share of total revenue
-- ==========================================================
WITH regional_totals AS (
    SELECT
        shipping_region AS region,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        ROUND(SUM(total_amount), 2) AS regional_revenue,
        ROUND(AVG(total_amount), 2) AS regional_aov,
        ROUND(SUM(estimated_profit), 2) AS regional_profit
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY shipping_region
)
SELECT
    region,
    total_orders,
    unique_customers,
    regional_revenue,
    ROUND(regional_revenue * 100.0 / SUM(regional_revenue) OVER(), 2) AS pct_of_global_revenue,
    regional_aov,
    regional_profit,
    ROUND((regional_profit / NULLIF(regional_revenue, 0)) * 100.0, 2) AS profit_margin_pct
FROM regional_totals
ORDER BY regional_revenue DESC;
