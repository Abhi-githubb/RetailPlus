-- ==========================================================
-- Customer: New vs Returning Customers Cohort Breakdown
-- Uses ROW_NUMBER() window function to classify first-time vs repeat purchases
-- ==========================================================
WITH order_sequence AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        SUBSTR(order_date, 1, 7) AS sales_month,
        total_amount,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS customer_order_seq
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
),
classified_orders AS (
    SELECT
        sales_month,
        order_id,
        customer_id,
        total_amount,
        CASE
            WHEN customer_order_seq = 1 THEN 'New Customer'
            ELSE 'Returning Customer'
        END AS customer_type
    FROM order_sequence
)
SELECT
    sales_month,
    customer_type,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM classified_orders
GROUP BY sales_month, customer_type
ORDER BY sales_month ASC, customer_type DESC;
