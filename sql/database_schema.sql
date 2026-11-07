-- ============================================================================
-- E-Commerce Product & Customer Behavior Analytics - Database Schema (DDL)
-- Database Engine Compatibility: PostgreSQL / SQLite / MySQL
-- ============================================================================

-- Drop existing tables if re-running script (Order respects Foreign Key dependency chain)
DROP TABLE IF EXISTS fact_order_reviews;
DROP TABLE IF EXISTS fact_order_payments;
DROP TABLE IF EXISTS fact_order_items;
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_sellers;
DROP TABLE IF EXISTS dim_customers;

-- 1. Customers Dimension Table
CREATE TABLE dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

-- 2. Sellers Dimension Table
CREATE TABLE dim_sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

-- 3. Products Dimension Table (Includes English Category Translations)
CREATE TABLE dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght FLOAT,
    product_description_lenght FLOAT,
    product_photos_qty FLOAT,
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT,
    product_category_name_english VARCHAR(100)
);

-- 4. Orders Fact Table (Header level lifecycle)
CREATE TABLE fact_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    actual_delivery_days FLOAT,
    estimated_delivery_days FLOAT,
    delivery_delay_days FLOAT,
    is_late_delivery INT,
    purchase_year INT,
    purchase_month INT,
    purchase_year_month VARCHAR(10),
    purchase_day_of_week VARCHAR(15),
    purchase_hour INT
);

-- 5. Order Line Items Fact Table (Line item financial details)
CREATE TABLE fact_order_items (
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    order_item_id INT,
    product_id VARCHAR(50) REFERENCES dim_products(product_id),
    seller_id VARCHAR(50) REFERENCES dim_sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price NUMERIC(10, 2),
    freight_value NUMERIC(10, 2),
    PRIMARY KEY (order_id, order_item_id)
);

-- 6. Order Payments Fact Table
CREATE TABLE fact_order_payments (
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    payment_sequential INT,
    payment_type VARCHAR(30),
    payment_installments INT,
    payment_value NUMERIC(10, 2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- 7. Order Reviews Fact Table
CREATE TABLE fact_order_reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    review_score INT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- Performance Indexes on Foreign Keys & Temporal Fields
CREATE INDEX idx_orders_customer_id ON fact_orders(customer_id);
CREATE INDEX idx_orders_purchase_timestamp ON fact_orders(order_purchase_timestamp);
CREATE INDEX idx_order_items_product_id ON fact_order_items(product_id);
CREATE INDEX idx_order_items_seller_id ON fact_order_items(seller_id);