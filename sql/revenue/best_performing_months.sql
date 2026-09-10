-- ==========================================================
-- Revenue: Best Performing Months Ranking
-- Uses DENSE_RANK() window function to identify record-breaking sales months
-- ==========================================================
WITH monthly_revenue AS (
    SELECT
        SUBSTR(order_date, 1, 7) AS sales_month,
        ROUND(SUM(total_amount), 2) AS total_revenue,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(AVG(total_amount), 2) AS aov,
        ROUND(SUM(estimated_profit), 2) AS total_profit
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY SUBSTR(order_date, 1, 7)
)
SELECT
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    sales_month,
    total_revenue,
    total_orders,
    aov,
    total_profit,
    ROUND((total_profit / NULLIF(total_revenue, 0)) * 100.0, 2) AS profit_margin_pct
FROM monthly_revenue
ORDER BY revenue_rank ASC
LIMIT 12;
