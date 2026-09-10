-- ==========================================================
-- Cohorts: Monthly Cohort Retention Matrix
-- Calculates customer retention rates across Month 0 to Month 12+
-- ==========================================================
WITH customer_cohort AS (
    SELECT
        customer_id,
        SUBSTR(MIN(order_date), 1, 7) AS cohort_month
    FROM orders
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY customer_id
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
customer_activities AS (
    SELECT
        o.customer_id,
        cc.cohort_month,
        SUBSTR(o.order_date, 1, 7) AS activity_month,
        (
            (CAST(SUBSTR(SUBSTR(o.order_date, 1, 7), 1, 4) AS INT) - CAST(SUBSTR(cc.cohort_month, 1, 4) AS INT)) * 12 +
            (CAST(SUBSTR(SUBSTR(o.order_date, 1, 7), 6, 2) AS INT) - CAST(SUBSTR(cc.cohort_month, 6, 2) AS INT))
        ) AS period_number
    FROM orders o
    JOIN customer_cohort cc ON o.customer_id = cc.customer_id
    WHERE o.order_status IN ('Completed', 'Shipped')
),
cohort_matrix AS (
    SELECT
        ca.cohort_month,
        cs.cohort_size,
        ca.period_number,
        COUNT(DISTINCT ca.customer_id) AS active_retained_customers
    FROM customer_activities ca
    JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
    GROUP BY ca.cohort_month, cs.cohort_size, ca.period_number
)
SELECT
    cohort_month,
    cohort_size,
    period_number AS month_offset,
    active_retained_customers,
    ROUND((active_retained_customers * 100.0 / cohort_size), 2) AS retention_rate_pct
FROM cohort_matrix
WHERE period_number >= 0
ORDER BY cohort_month ASC, month_offset ASC;
