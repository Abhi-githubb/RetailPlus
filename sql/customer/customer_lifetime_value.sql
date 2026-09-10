-- ==========================================================
-- Customer: Customer Lifetime Value (CLV) Distribution & Tiers
-- Segments customers into value tiers (VIP, High, Mid, Low) based on historical spend
-- ==========================================================
WITH customer_clv AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS lifetime_value,
        ROUND(AVG(o.total_amount), 2) AS customer_aov
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY c.customer_id, c.name, c.region
),
clv_brackets AS (
    SELECT
        customer_id,
        lifetime_value,
        total_orders,
        CASE
            WHEN lifetime_value >= 1500 THEN 'VIP Tier ($1,500+)'
            WHEN lifetime_value >= 750 THEN 'High Value ($750 - $1,499)'
            WHEN lifetime_value >= 250 THEN 'Mid Value ($250 - $749)'
            ELSE 'Standard (< $250)'
        END AS clv_segment
    FROM customer_clv
)
SELECT
    clv_segment,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(), 2) AS pct_of_customer_base,
    ROUND(SUM(lifetime_value), 2) AS segment_total_revenue,
    ROUND(SUM(lifetime_value) * 100.0 / SUM(SUM(lifetime_value)) OVER(), 2) AS pct_of_total_revenue,
    ROUND(AVG(lifetime_value), 2) AS avg_clv_in_tier,
    ROUND(AVG(total_orders), 1) AS avg_orders_in_tier
FROM clv_brackets
GROUP BY clv_segment
ORDER BY segment_total_revenue DESC;
