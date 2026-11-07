WITH customer_orders AS (
    SELECT o.customer_id, o.order_id, SUM(oi.quantity * oi.price) AS order_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.customer_id, o.order_id
)
SELECT c.customer_id, c.customer_city, c.customer_country,
       COUNT(co.order_id) AS order_count,
       SUM(co.order_revenue) AS lifetime_revenue,
       AVG(co.order_revenue) AS average_order_value
FROM customers c
LEFT JOIN customer_orders co ON co.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_city, c.customer_country
ORDER BY lifetime_revenue DESC NULLS LAST;
