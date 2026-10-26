-- ==============================================================================
-- RetailPulse: Analytical Business Queries (SQLite)
-- Database: data/processed/retailpulse.db
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Total Sales Revenue, Returns, Net Revenue & Volume Summary
-- Business Question: What is the total financial performance of the business,
-- distinguishing between gross sales, customer returns, and net commercial revenue?
-- Concepts Demonstrated: Aggregations (SUM, COUNT), CASE WHEN, ROUND
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(*) AS total_transaction_lines,
    ROUND(SUM(CASE WHEN is_return = 0 THEN line_total ELSE 0 END), 2) AS gross_sales_gbp,
    ROUND(SUM(CASE WHEN is_return = 1 THEN line_total ELSE 0 END), 2) AS return_refunds_gbp,
    ROUND(SUM(line_total), 2) AS net_revenue_gbp,
    ROUND(ABS(SUM(CASE WHEN is_return = 1 THEN line_total ELSE 0 END)) * 100.0 / 
          SUM(CASE WHEN is_return = 0 THEN line_total ELSE 0 END), 2) AS refund_rate_pct,
    SUM(quantity) AS net_units_sold
FROM fact_sales;


-- ------------------------------------------------------------------------------
-- QUERY 2: Monthly Net Revenue Trends & Order Volume
-- Business Question: How has net sales revenue, order count, and average daily sales
-- evolved month-over-month across the 2010-2011 trading period?
-- Concepts Demonstrated: INNER JOIN, GROUP BY, Date-based Aggregation, ORDER BY
-- ------------------------------------------------------------------------------
SELECT 
    d.year_month,
    d.year,
    d.month_name,
    COUNT(DISTINCT f.invoice_no) AS monthly_orders,
    SUM(f.quantity) AS net_units_sold,
    ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END), 2) AS gross_revenue_gbp,
    ROUND(SUM(CASE WHEN f.is_return = 1 THEN f.line_total ELSE 0 END), 2) AS refund_value_gbp,
    ROUND(SUM(f.line_total), 2) AS net_revenue_gbp
FROM fact_sales f
INNER JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year_month, d.year, d.month_name
ORDER BY d.year_month ASC;


-- ------------------------------------------------------------------------------
-- QUERY 3: Quarterly and Yearly Financial Performance
-- Business Question: What is the high-level quarterly revenue trajectory and how
-- does performance compare across calendar quarters?
-- Concepts Demonstrated: Multi-level GROUP BY, INNER JOIN, SUM with CASE WHEN
-- ------------------------------------------------------------------------------
SELECT 
    d.year,
    d.quarter,
    d.year_quarter,
    COUNT(DISTINCT f.invoice_no) AS distinct_invoices,
    ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END), 2) AS gross_sales_gbp,
    ROUND(SUM(CASE WHEN f.is_return = 1 THEN f.line_total ELSE 0 END), 2) AS returns_gbp,
    ROUND(SUM(f.line_total), 2) AS net_revenue_gbp
FROM fact_sales f
INNER JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.quarter, d.year_quarter
ORDER BY d.year, d.quarter;


-- ------------------------------------------------------------------------------
-- QUERY 4: Top 10 Best-Selling Products by Unit Volume
-- Business Question: Which merchandise items generate the highest physical demand
-- and customer order frequency?
-- Concepts Demonstrated: INNER JOIN, GROUP BY, HAVING, ORDER BY, LIMIT
-- ------------------------------------------------------------------------------
SELECT 
    p.stock_code,
    p.description,
    p.avg_unit_price,
    SUM(f.quantity) AS total_units_sold,
    COUNT(DISTINCT f.invoice_no) AS order_appearances,
    ROUND(SUM(f.line_total), 2) AS net_product_revenue_gbp
FROM fact_sales f
INNER JOIN dim_product p ON f.stock_code = p.stock_code
WHERE f.is_return = 0
GROUP BY p.stock_code, p.description, p.avg_unit_price
HAVING total_units_sold > 0
ORDER BY total_units_sold DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 5: Top 10 Products by Net Revenue Contribution & Share of Total
-- Business Question: Which products are our biggest financial revenue drivers,
-- and what percentage of overall business sales does each top product represent?
-- Concepts Demonstrated: CTE (Common Table Expression), Window Function (SUM OVER)
-- ------------------------------------------------------------------------------
WITH ProductSales AS (
    SELECT 
        p.stock_code,
        p.description,
        ROUND(SUM(f.line_total), 2) AS product_net_revenue,
        SUM(f.quantity) AS units_sold,
        COUNT(DISTINCT f.invoice_no) AS order_appearances
    FROM fact_sales f
    INNER JOIN dim_product p ON f.stock_code = p.stock_code
    GROUP BY p.stock_code, p.description
)
SELECT 
    stock_code,
    description,
    units_sold,
    order_appearances,
    product_net_revenue,
    ROUND(product_net_revenue * 100.0 / (SELECT SUM(line_total) FROM fact_sales), 2) AS pct_of_total_revenue
FROM ProductSales
ORDER BY product_net_revenue DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 6: Country-Level Revenue & Market Region Segmentation
-- Business Question: How does revenue break down across geographic markets (Domestic UK,
-- European Union, and International Export), and what is the market share of each?
-- Concepts Demonstrated: INNER JOIN, GROUP BY, Window Function for Market Share %
-- ------------------------------------------------------------------------------
SELECT 
    g.market_region,
    g.country,
    COUNT(DISTINCT f.invoice_no) AS total_orders,
    COUNT(DISTINCT f.customer_id) AS active_customers,
    ROUND(SUM(f.line_total), 2) AS net_revenue_gbp,
    ROUND(SUM(f.line_total) * 100.0 / (SELECT SUM(line_total) FROM fact_sales), 2) AS pct_global_revenue
FROM fact_sales f
INNER JOIN dim_geography g ON f.country_key = g.country_key
GROUP BY g.market_region, g.country
ORDER BY net_revenue_gbp DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- QUERY 7: Average Order Value (AOV) by Geographic Market Region
-- Business Question: What is the typical basket size / average expenditure per order,
-- and do international export orders yield higher transaction values than domestic UK?
-- Concepts Demonstrated: CTE for Order-Level Aggregation, Multi-level Aggregation, AVG
-- ------------------------------------------------------------------------------
WITH OrderLevelMetrics AS (
    SELECT 
        f.invoice_no,
        g.market_region,
        SUM(f.line_total) AS order_total_gbp,
        SUM(f.quantity) AS order_units
    FROM fact_sales f
    INNER JOIN dim_geography g ON f.country_key = g.country_key
    WHERE f.is_return = 0
    GROUP BY f.invoice_no, g.market_region
)
SELECT 
    market_region,
    COUNT(invoice_no) AS completed_orders,
    ROUND(SUM(order_total_gbp), 2) AS total_revenue_gbp,
    ROUND(AVG(order_total_gbp), 2) AS average_order_value_gbp,
    ROUND(AVG(order_units), 1) AS avg_items_per_order
FROM OrderLevelMetrics
GROUP BY market_region
ORDER BY average_order_value_gbp DESC;


-- ------------------------------------------------------------------------------
-- QUERY 8: Unique Customer Count (Registered Loyalty Accounts vs. Guest Checkouts)
-- Business Question: How many distinct purchasing customers exist, and what is the
-- ratio between registered recurring customers and unauthenticated guest checkouts?
-- Concepts Demonstrated: LEFT JOIN, CASE WHEN, COUNT(DISTINCT)
-- ------------------------------------------------------------------------------
SELECT 
    c.customer_type,
    COUNT(DISTINCT CASE WHEN f.customer_id != -1 THEN f.customer_id ELSE NULL END) AS unique_registered_accounts,
    COUNT(DISTINCT f.invoice_no) AS total_orders_placed,
    COUNT(*) AS transaction_lines,
    ROUND(SUM(f.line_total), 2) AS total_spend_gbp,
    ROUND(SUM(f.line_total) * 100.0 / (SELECT SUM(line_total) FROM fact_sales), 2) AS revenue_share_pct
FROM fact_sales f
INNER JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_type;


-- ------------------------------------------------------------------------------
-- QUERY 9: Impact of Missing Customer IDs (Guest Checkout Revenue Risk)
-- Business Question: Exactly how much commercial revenue, order volume, and unit
-- volume would be lost if an analyst erroneously dropped all missing Customer IDs?
-- Concepts Demonstrated: Explicit Comparison, CASE WHEN, Percentage Impact
-- ------------------------------------------------------------------------------
SELECT 
    CASE WHEN customer_id = -1 THEN 'Guest Checkout (Missing CustomerID)' 
         ELSE 'Registered Customer Account' END AS checkout_category,
    COUNT(DISTINCT invoice_no) AS distinct_invoices,
    COUNT(*) AS line_item_records,
    SUM(quantity) AS net_units_sold,
    ROUND(SUM(line_total), 2) AS net_revenue_gbp,
    ROUND(SUM(line_total) * 100.0 / (SELECT SUM(line_total) FROM fact_sales), 2) AS revenue_contribution_pct
FROM fact_sales
GROUP BY checkout_category;


-- ------------------------------------------------------------------------------
-- QUERY 10: Customer Purchase Frequency & Repeat Customer Distribution
-- Business Question: What percentage of our registered customer base are one-time
-- buyers versus multi-order repeat customers?
-- Concepts Demonstrated: CTE, CASE WHEN Binning, Aggregate Percentage Calculation
-- ------------------------------------------------------------------------------
WITH CustomerFrequency AS (
    SELECT 
        customer_id,
        total_orders,
        total_spend,
        CASE 
            WHEN total_orders = 1 THEN '1 Order (One-Time Buyer)'
            WHEN total_orders BETWEEN 2 AND 5 THEN '2-5 Orders (Repeat Customer)'
            WHEN total_orders BETWEEN 6 AND 10 THEN '6-10 Orders (Loyal Customer)'
            ELSE '10+ Orders (VIP / Power Buyer)'
        END AS loyalty_tier
    FROM dim_customer
    WHERE customer_id != -1
)
SELECT 
    loyalty_tier,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customer WHERE customer_id != -1), 2) AS customer_pct,
    ROUND(SUM(total_spend), 2) AS tier_revenue_gbp,
    ROUND(SUM(total_spend) * 100.0 / (SELECT SUM(total_spend) FROM dim_customer WHERE customer_id != -1), 2) AS revenue_pct
FROM CustomerFrequency
GROUP BY loyalty_tier
ORDER BY customer_count DESC;


-- ------------------------------------------------------------------------------
-- QUERY 11: New vs. Returning Customer Monthly Acquisition Cohort
-- Business Question: In each calendar month, how much revenue was generated by
-- brand-new customer acquisitions versus returning repeat customers?
-- Concepts Demonstrated: CTEs, Subquery Join, Date Parsing, Cohort Identification
-- ------------------------------------------------------------------------------
WITH CustomerCohorts AS (
    SELECT 
        customer_id,
        SUBSTR(first_order_date, 1, 7) AS cohort_month
    FROM dim_customer
    WHERE customer_id != -1
),
MonthlyCustomerSpend AS (
    SELECT 
        d.year_month,
        f.customer_id,
        c.cohort_month,
        CASE WHEN d.year_month = c.cohort_month THEN 'New Customer' ELSE 'Returning Customer' END AS buyer_status,
        f.line_total
    FROM fact_sales f
    INNER JOIN dim_date d ON f.date_key = d.date_key
    INNER JOIN CustomerCohorts c ON f.customer_id = c.customer_id
    WHERE f.customer_id != -1
)
SELECT 
    year_month,
    buyer_status,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(line_total), 2) AS cohort_revenue_gbp
FROM MonthlyCustomerSpend
GROUP BY year_month, buyer_status
ORDER BY year_month ASC, buyer_status DESC;


-- ------------------------------------------------------------------------------
-- QUERY 12: Top 10 Registered Customers by Lifetime Revenue
-- Business Question: Who are our top 10 most valuable client accounts, where are
-- they located, and what is their order frequency?
-- Concepts Demonstrated: INNER JOIN, Filtering Sentinels, ORDER BY, LIMIT
-- ------------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.country,
    c.customer_type,
    c.total_orders,
    c.total_items_bought,
    c.first_order_date,
    c.last_order_date,
    ROUND(c.total_spend, 2) AS lifetime_spend_gbp
FROM dim_customer c
WHERE c.customer_id != -1
ORDER BY c.total_spend DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 13: Customer Revenue Ranking and Decile Segmentation (Window Functions)
-- Business Question: How do registered customers rank relative to one another,
-- and what are the cut-offs for the top 10% (Decile 1) of our client base?
-- Concepts Demonstrated: Window Functions (ROW_NUMBER, DENSE_RANK, NTILE)
-- ------------------------------------------------------------------------------
WITH RankedCustomers AS (
    SELECT 
        customer_id,
        country,
        total_orders,
        ROUND(total_spend, 2) AS total_spend_gbp,
        ROW_NUMBER() OVER (ORDER BY total_spend DESC) AS revenue_rank,
        DENSE_RANK() OVER (ORDER BY total_spend DESC) AS dense_rank,
        NTILE(10) OVER (ORDER BY total_spend DESC) AS spend_decile
    FROM dim_customer
    WHERE customer_id != -1
)
SELECT 
    revenue_rank,
    customer_id,
    country,
    total_orders,
    total_spend_gbp,
    spend_decile,
    CASE WHEN spend_decile = 1 THEN 'Top 10% VIP Tier'
         WHEN spend_decile <= 3 THEN 'Top 30% Core Tier'
         ELSE 'Remaining 70% Mass Tier' END AS strategic_segment
FROM RankedCustomers
WHERE revenue_rank <= 15 OR revenue_rank IN (100, 500, 1000)
ORDER BY revenue_rank ASC;


-- ------------------------------------------------------------------------------
-- QUERY 14: Running Cumulative Monthly Revenue (Running Total Window Function)
-- Business Question: How did total revenue accumulate day-by-day or month-by-month
-- throughout the entire year of 2011?
-- Concepts Demonstrated: Window Function (SUM OVER ROWS BETWEEN UNBOUNDED PRECEDING)
-- ------------------------------------------------------------------------------
WITH MonthlyTotals AS (
    SELECT 
        d.year_month,
        ROUND(SUM(f.line_total), 2) AS monthly_net_revenue
    FROM fact_sales f
    INNER JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year_month
)
SELECT 
    year_month,
    monthly_net_revenue,
    ROUND(SUM(monthly_net_revenue) OVER (
        ORDER BY year_month 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS cumulative_running_revenue_gbp
FROM MonthlyTotals
ORDER BY year_month ASC;


-- ------------------------------------------------------------------------------
-- QUERY 15: Returns and Cancellation Rate Analysis by Major Country Market
-- Business Question: What is the cancellation/return rate percentage across our
-- major country markets, and which international regions suffer the highest refund burden?
-- Concepts Demonstrated: CTE, Aggregations with CASE WHEN, HAVING Filter, Sorting by Rate
-- ------------------------------------------------------------------------------
WITH MarketReturnMetrics AS (
    SELECT 
        g.country,
        g.market_region,
        COUNT(DISTINCT f.invoice_no) AS total_orders,
        ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END), 2) AS gross_sales,
        ROUND(ABS(SUM(CASE WHEN f.is_return = 1 THEN f.line_total ELSE 0 END)), 2) AS return_refund_val,
        SUM(CASE WHEN f.is_return = 1 THEN 1 ELSE 0 END) AS return_line_count,
        COUNT(*) AS total_line_count
    FROM fact_sales f
    INNER JOIN dim_geography g ON f.country_key = g.country_key
    GROUP BY g.country, g.market_region
    HAVING gross_sales > 10000.00
)
SELECT 
    country,
    market_region,
    total_orders,
    gross_sales,
    return_refund_val,
    ROUND(return_refund_val * 100.0 / gross_sales, 2) AS refund_value_rate_pct,
    ROUND(return_line_count * 100.0 / total_line_count, 2) AS return_frequency_pct
FROM MarketReturnMetrics
ORDER BY refund_value_rate_pct DESC;
