-- ==========================================================
-- Revenue: Month-over-Month (MoM) Revenue Growth Rate
-- Leverages LAG() window function to calculate percentage deltas
-- ==========================================================
WITH monthly_metrics AS (
    SELECT
        SUBSTR(order_date, 1, 7) AS sales_month,
        ROUND(SUM(total_amount), 2) AS current_revenue,
        COUNT(DISTINCT order_id) AS current_orders
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY SUBSTR(order_date, 1, 7)
),
growth_calc AS (
    SELECT
        sales_month,
        current_revenue,
        LAG(current_revenue, 1) OVER (ORDER BY sales_month) AS prior_month_revenue,
        current_orders,
        LAG(current_orders, 1) OVER (ORDER BY sales_month) AS prior_month_orders
    FROM monthly_metrics
)
SELECT
    sales_month,
    current_revenue,
    prior_month_revenue,
    ROUND(
        CASE
            WHEN prior_month_revenue IS NOT NULL AND prior_month_revenue > 0
            THEN ((current_revenue - prior_month_revenue) / prior_month_revenue) * 100.0
            ELSE 0.0
        END, 2
    ) AS mom_revenue_growth_pct,
    current_orders,
    prior_month_orders,
    ROUND(
        CASE
            WHEN prior_month_orders IS NOT NULL AND prior_month_orders > 0
            THEN ((current_orders - prior_month_orders) * 100.0) / prior_month_orders
            ELSE 0.0
        END, 2
    ) AS mom_order_growth_pct
FROM growth_calc
ORDER BY sales_month ASC;
