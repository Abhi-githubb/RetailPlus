-- ==========================================================
-- Revenue: Year-over-Year (YoY) Performance Comparison
-- Compares revenue of the same month across consecutive years using LAG(12)
-- ==========================================================
WITH monthly_data AS (
    SELECT
        SUBSTR(order_date, 1, 7) AS sales_month,
        SUBSTR(order_date, 1, 4) AS sales_year,
        SUBSTR(order_date, 6, 2) AS calendar_month,
        ROUND(SUM(total_amount), 2) AS revenue,
        COUNT(DISTINCT order_id) AS orders_count
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY SUBSTR(order_date, 1, 7), SUBSTR(order_date, 1, 4), SUBSTR(order_date, 6, 2)
),
yoy_lag AS (
    SELECT
        sales_month,
        sales_year,
        calendar_month,
        revenue,
        LAG(revenue, 12) OVER (ORDER BY sales_month) AS prior_year_revenue,
        orders_count,
        LAG(orders_count, 12) OVER (ORDER BY sales_month) AS prior_year_orders
    FROM monthly_data
)
SELECT
    sales_month,
    revenue AS current_year_revenue,
    prior_year_revenue,
    ROUND(
        CASE
            WHEN prior_year_revenue IS NOT NULL AND prior_year_revenue > 0
            THEN ((revenue - prior_year_revenue) / prior_year_revenue) * 100.0
            ELSE NULL
        END, 2
    ) AS yoy_growth_pct,
    orders_count,
    prior_year_orders
FROM yoy_lag
WHERE prior_year_revenue IS NOT NULL
ORDER BY sales_month ASC;
