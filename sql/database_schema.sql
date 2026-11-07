-- Generic relational model; adapt types and names to the source system.
CREATE TABLE customers (
    customer_id VARCHAR(128) PRIMARY KEY,
    customer_created_at TIMESTAMP,
    customer_city VARCHAR(255),
    customer_country VARCHAR(255)
);

CREATE TABLE products (
    product_id VARCHAR(128) PRIMARY KEY,
    product_name VARCHAR(512),
    category VARCHAR(255)
);

CREATE TABLE orders (
    order_id VARCHAR(128) PRIMARY KEY,
    customer_id VARCHAR(128) NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP,
    order_status VARCHAR(64)
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id VARCHAR(128) NOT NULL REFERENCES orders(order_id),
    product_id VARCHAR(128) NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    price DECIMAL(12, 2) NOT NULL
);
