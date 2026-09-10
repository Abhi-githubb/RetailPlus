-- ==========================================================
-- RetailPulse Relational Database Schema (PostgreSQL DDL)
-- Production E-Commerce Analytics Data Warehouse
-- ==========================================================

-- Drop existing tables (idempotent setup)
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- 1. Customers Table
CREATE TABLE customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL,
    signup_date TIMESTAMP NOT NULL,
    country VARCHAR(64) NOT NULL,
    region VARCHAR(64) NOT NULL,
    acquisition_channel VARCHAR(64) NOT NULL
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_customers_signup ON customers(signup_date);
CREATE INDEX idx_customers_channel ON customers(acquisition_channel);

-- 2. Products Table
CREATE TABLE products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    subcategory VARCHAR(64) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    cost NUMERIC(10, 2) NOT NULL CHECK (cost >= 0),
    launch_date DATE NOT NULL
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_subcategory ON products(subcategory);

-- 3. Orders Table
CREATE TABLE orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date TIMESTAMP NOT NULL,
    order_status VARCHAR(32) NOT NULL CHECK (order_status IN ('Completed', 'Shipped', 'Processing', 'Cancelled', 'Refunded')),
    shipping_region VARCHAR(64) NOT NULL,
    payment_method VARCHAR(64) NOT NULL,
    discount NUMERIC(10, 2) DEFAULT 0.0 CHECK (discount >= 0),
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    total_items INTEGER DEFAULT 1 CHECK (total_items >= 0),
    unique_products INTEGER DEFAULT 1 CHECK (unique_products >= 0),
    estimated_profit NUMERIC(10, 2) DEFAULT 0.0
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_region ON orders(shipping_region);
CREATE INDEX idx_orders_analytics ON orders(order_date, order_status, shipping_region);

-- 4. Order Items Table
CREATE TABLE order_items (
    order_item_id VARCHAR(32) PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount NUMERIC(10, 2) DEFAULT 0.0 CHECK (discount >= 0),
    product_cost NUMERIC(10, 2) DEFAULT 0.0,
    total_cost NUMERIC(10, 2) DEFAULT 0.0,
    gross_amount NUMERIC(10, 2) DEFAULT 0.0,
    net_amount NUMERIC(10, 2) DEFAULT 0.0,
    profit NUMERIC(10, 2) DEFAULT 0.0
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- 5. Payments Table
CREATE TABLE payments (
    payment_id VARCHAR(32) PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_date TIMESTAMP NOT NULL,
    payment_method VARCHAR(64) NOT NULL,
    payment_status VARCHAR(32) NOT NULL CHECK (payment_status IN ('Success', 'Failed', 'Refunded', 'Pending')),
    payment_amount NUMERIC(10, 2) NOT NULL CHECK (payment_amount >= 0)
);

CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(payment_status);

-- 6. Returns Table
CREATE TABLE returns (
    return_id VARCHAR(32) PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    return_date TIMESTAMP NOT NULL,
    return_reason VARCHAR(128) NOT NULL,
    refund_amount NUMERIC(10, 2) NOT NULL CHECK (refund_amount >= 0)
);

CREATE INDEX idx_returns_order ON returns(order_id);
CREATE INDEX idx_returns_product ON returns(product_id);
CREATE INDEX idx_returns_date ON returns(return_date);
