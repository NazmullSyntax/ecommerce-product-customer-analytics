-- Replace table/column names if your source schema differs.
SELECT 'customers' AS table_name, COUNT(*) AS row_count,
       COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_customer_ids
FROM customers;

SELECT
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_ids,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS missing_order_dates
FROM orders;

SELECT COUNT(*) AS invalid_order_items
FROM order_items
WHERE quantity IS NULL OR quantity <= 0 OR price IS NULL OR price < 0;

SELECT oi.order_id, oi.product_id
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
LEFT JOIN products p ON p.product_id = oi.product_id
WHERE o.order_id IS NULL OR p.product_id IS NULL;
