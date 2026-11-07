SELECT p.product_id, p.product_name, p.category,
       SUM(oi.quantity) AS units_sold,
       SUM(oi.quantity * oi.price) AS revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC;

SELECT p.category, SUM(oi.quantity * oi.price) AS revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;
