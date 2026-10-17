-- ==============================================================================
-- RetailPulse: Relational Star Schema DDL (SQLite)
-- Database: data/processed/retailpulse.db
-- ==============================================================================

PRAGMA foreign_keys = OFF;

-- Drop child fact table first, then dimension tables
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_geography;

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------------------------
-- 1. Dimension Tables
-- ------------------------------------------------------------------------------

-- DimDate: Calendar Dimension for Time Intelligence
CREATE TABLE dim_date (
    date_key        INTEGER PRIMARY KEY,            -- Format: YYYYMMDD (e.g. 20101201)
    order_date      TEXT NOT NULL,                  -- Format: YYYY-MM-DD
    year            INTEGER NOT NULL,               -- 2010, 2011
    quarter         INTEGER NOT NULL,               -- 1, 2, 3, 4
    year_quarter    TEXT NOT NULL,                  -- e.g. '2011-Q1'
    month           INTEGER NOT NULL,               -- 1 to 12
    month_name      TEXT NOT NULL,                  -- 'January' to 'December'
    year_month      TEXT NOT NULL,                  -- e.g. '2011-01'
    day_of_week     INTEGER NOT NULL,               -- 1 (Monday) to 7 (Sunday)
    day_name        TEXT NOT NULL                   -- 'Monday' to 'Sunday'
);

-- DimGeography: Geographic Hierarchy & Market Segmentation
CREATE TABLE dim_geography (
    country_key     INTEGER PRIMARY KEY,            -- 1 to 38
    country         TEXT NOT NULL UNIQUE,           -- Country name (e.g. 'United Kingdom')
    market_region   TEXT NOT NULL                   -- 'Domestic UK', 'European Union', 'International Export'
);

-- DimProduct: Merchandise Catalog Dimension
CREATE TABLE dim_product (
    stock_code          TEXT PRIMARY KEY,           -- SKU identifier (e.g. '85123A')
    description         TEXT NOT NULL,              -- Item description
    avg_unit_price      REAL NOT NULL,              -- Historical average price in GBP
    min_unit_price      REAL NOT NULL,              -- Minimum unit price observed
    max_unit_price      REAL NOT NULL,              -- Maximum unit price observed
    total_units_sold    INTEGER NOT NULL,           -- Cumulative units sold across all orders
    total_revenue       REAL NOT NULL               -- Cumulative revenue generated in GBP
);

-- DimCustomer: Customer Profile & Lifetime Summary
CREATE TABLE dim_customer (
    customer_id         INTEGER PRIMARY KEY,        -- 5-digit ID (-1 represents Guest Checkouts)
    country             TEXT NOT NULL,              -- Primary country of customer
    first_order_date    TEXT NOT NULL,              -- Date of earliest purchase
    last_order_date     TEXT NOT NULL,              -- Date of most recent purchase
    total_orders        INTEGER NOT NULL,           -- Distinct invoice count
    total_items_bought  INTEGER NOT NULL,           -- Net units purchased
    total_spend         REAL NOT NULL,              -- Net monetary spend in GBP
    customer_type       TEXT NOT NULL               -- 'Registered' or 'Guest Checkout'
);

-- ------------------------------------------------------------------------------
-- 2. Fact Table
-- ------------------------------------------------------------------------------

-- FactSales: Order Line-Item Grain (Sales and Returns)
CREATE TABLE fact_sales (
    sale_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no          TEXT NOT NULL,              -- Transaction ID (starts with 'C' for returns)
    invoice_date        TEXT NOT NULL,              -- Exact timestamp: YYYY-MM-DD HH:MM:SS
    date_key            INTEGER NOT NULL,           -- FK -> dim_date.date_key
    customer_id         INTEGER NOT NULL,           -- FK -> dim_customer.customer_id
    stock_code          TEXT NOT NULL,              -- FK -> dim_product.stock_code
    country_key         INTEGER NOT NULL,           -- FK -> dim_geography.country_key
    quantity            INTEGER NOT NULL,           -- Units (> 0 for sales, < 0 for returns)
    unit_price          REAL NOT NULL,              -- Price per unit in GBP
    line_total          REAL NOT NULL,              -- quantity * unit_price
    is_return           INTEGER NOT NULL,           -- 1 if return, 0 if sale
    transaction_type    TEXT NOT NULL,              -- 'Sale' or 'Return'
    FOREIGN KEY (date_key)    REFERENCES dim_date (date_key),
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    FOREIGN KEY (stock_code)  REFERENCES dim_product (stock_code),
    FOREIGN KEY (country_key) REFERENCES dim_geography (country_key)
);

-- ------------------------------------------------------------------------------
-- 3. Performance Indexes
-- ------------------------------------------------------------------------------
CREATE INDEX idx_fact_date_key         ON fact_sales (date_key);
CREATE INDEX idx_fact_customer_id      ON fact_sales (customer_id);
CREATE INDEX idx_fact_stock_code       ON fact_sales (stock_code);
CREATE INDEX idx_fact_country_key      ON fact_sales (country_key);
CREATE INDEX idx_fact_invoice_no       ON fact_sales (invoice_no);
CREATE INDEX idx_fact_transaction_type ON fact_sales (transaction_type);
CREATE INDEX idx_date_year_month       ON dim_date (year_month);
