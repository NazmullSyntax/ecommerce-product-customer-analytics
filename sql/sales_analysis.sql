-- Monthly completed-order revenue.
SELECT DATE_TRUNC('month', o.order_date) AS month,
       SUM(oi.quantity * oi.price) AS revenue,
       COUNT(DISTINCT o.order_id) AS order_count
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'completed'
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;

-- Average order value.
WITH order_totals AS (
    SELECT o.order_id, SUM(oi.quantity * oi.price) AS order_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.order_id
)
SELECT AVG(order_revenue) AS average_order_value FROM order_totals;
