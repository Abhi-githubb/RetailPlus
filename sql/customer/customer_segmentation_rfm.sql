-- ==========================================================
-- Customer: RFM (Recency, Frequency, Monetary) Segmentation
-- Uses NTILE() and CASE logic to partition customer portfolio into actionable behavioral cohorts
-- ==========================================================
WITH customer_rfm_raw AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        COUNT(o.order_id) AS frequency,
        ROUND(SUM(o.total_amount), 2) AS monetary,
        MAX(o.order_date) AS last_order_date
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY c.customer_id, c.name, c.region
),
rfm_scores AS (
    SELECT
        customer_id,
        name,
        region,
        frequency,
        monetary,
        last_order_date,
        NTILE(4) OVER (ORDER BY last_order_date ASC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_rfm_raw
),
rfm_segments AS (
    SELECT
        customer_id,
        name,
        region,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        CASE
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score = 1 THEN 'Recent Potential'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Need Attention'
            ELSE 'Hibernating / Dormant'
        END AS rfm_segment
    FROM rfm_scores
)
SELECT
    rfm_segment,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(), 2) AS pct_of_customers,
    ROUND(SUM(monetary), 2) AS total_segment_revenue,
    ROUND(AVG(monetary), 2) AS avg_monetary_value,
    ROUND(AVG(frequency), 1) AS avg_order_frequency
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_segment_revenue DESC;
