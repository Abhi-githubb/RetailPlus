-- ==========================================================
-- Revenue: Promotional Discount Impact and Price Elasticity
-- Evaluates discount bracket volume, revenue retention, and margins
-- ==========================================================
WITH discounted_orders AS (
    SELECT
        order_id,
        total_amount,
        discount,
        estimated_profit,
        ROUND((discount / NULLIF(total_amount + discount, 0)) * 100.0, 1) AS effective_discount_pct,
        CASE
            WHEN discount = 0 THEN '0% Full Price'
            WHEN (discount / NULLIF(total_amount + discount, 0)) <= 0.05 THEN '1% - 5% Low'
            WHEN (discount / NULLIF(total_amount + discount, 0)) <= 0.15 THEN '6% - 15% Medium'
            ELSE '> 15% High Promotion'
        END AS discount_tier
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
)
SELECT
    discount_tier,
    COUNT(order_id) AS order_count,
    ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER(), 2) AS pct_of_orders,
    ROUND(SUM(total_amount), 2) AS net_revenue,
    ROUND(SUM(discount), 2) AS total_discount_given,
    ROUND(AVG(total_amount), 2) AS tier_aov,
    ROUND(SUM(estimated_profit), 2) AS total_profit,
    ROUND((SUM(estimated_profit) / NULLIF(SUM(total_amount), 0)) * 100.0, 2) AS net_margin_pct
FROM discounted_orders
GROUP BY discount_tier
ORDER BY net_revenue DESC;
