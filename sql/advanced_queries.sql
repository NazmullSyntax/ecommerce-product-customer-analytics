-- Repeat purchase rate among customers with at least one completed order.
WITH customer_order_counts AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id
)
SELECT 100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
       / NULLIF(COUNT(*), 0) AS repeat_purchase_rate_pct
FROM customer_order_counts;

-- Monthly cohort retention by first completed purchase month.
WITH first_purchase AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', order_date) AS activity_month
    FROM orders
    WHERE order_status = 'completed'
)
SELECT fp.cohort_month, a.activity_month,
       COUNT(DISTINCT a.customer_id) AS active_customers
FROM first_purchase fp
JOIN activity a ON a.customer_id = fp.customer_id
GROUP BY fp.cohort_month, a.activity_month
ORDER BY fp.cohort_month, a.activity_month;
