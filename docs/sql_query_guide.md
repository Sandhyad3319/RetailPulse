# RetailPulse: SQL Analytical Query Reference Guide

This reference guide documents all 15 production business queries executed against the SQLite database (`data/processed/retailpulse.db`), detailing the business question, advanced SQL techniques, and actual output results.

---

## Query Directory

| Query # | Query Title | Core SQL Techniques | Business Domain |
| :---: | :--- | :--- | :--- |
| **Q1** | **Total Sales & Revenue Summary** | `SUM`, `CASE WHEN`, Aggregations | Executive Performance |
| **Q2** | **Monthly Revenue & Volume Trends** | `INNER JOIN`, Date Grouping | Time Series / Growth |
| **Q3** | **Quarterly & Yearly Performance** | Multi-level `GROUP BY`, `CASE WHEN` | Financial Reporting |
| **Q4** | **Top 10 Products by Unit Volume** | `INNER JOIN`, `HAVING`, `LIMIT` | Inventory / Demand |
| **Q5** | **Top 10 Products by Revenue Share** | CTE, Window Function (`SUM OVER`) | Product Pareto |
| **Q6** | **Country-Level Revenue Breakdown** | `JOIN`, Window Function Share % | Geographic Strategy |
| **Q7** | **Average Order Value (AOV) by Region** | Multi-level CTE, `AVG`, Basket Size | Unit Economics |
| **Q8** | **Customer Account Segmentation** | `LEFT JOIN`, `CASE WHEN`, Sentinel check | Customer Intelligence |
| **Q9** | **Guest Checkout Financial Risk** | Revenue contribution analysis | Data Governance |
| **Q10** | **Purchase Frequency Distribution** | CTE, `CASE WHEN` Bins, Share % | Customer Retention |
| **Q11** | **New vs. Returning Customer Cohorts** | Cohort CTE, Month Matching | Customer Acquisition |
| **Q12** | **Top 10 Registered Customers** | Filtering, Ordering, Lifetime Value | VIP Account Management |
| **Q13** | **Customer Revenue Deciles & Ranking** | `ROW_NUMBER`, `DENSE_RANK`, `NTILE(10)` | Advanced Analytics |
| **Q14** | **Running Cumulative Revenue** | Window Function (`ROWS BETWEEN`) | Executive Pace Tracking |
| **Q15** | **Returns & Cancellation Rate by Country** | CTE, Rate Calculation, `HAVING` | Operational Risk |

---

## Detailed Query Walkthroughs

### Query 1: Total Sales Revenue, Returns & Net Commercial Revenue
**Business Question**: What is the overall financial performance of the business, separating gross revenue from returns?

```sql
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
```
**Actual Result**:
- Total Orders: **23,796**
- Total Lines: **534,129**
- Gross Sales: **£10,642,110.80**
- Returns/Refunds: **-£893,979.73**
- Net Revenue: **£9,748,131.07**
- Refund Rate: **8.40%**
- Net Units Sold: **5,296,860**

---

### Query 5: Top Products by Revenue Contribution & Share of Total
**Business Question**: Which products are the primary financial drivers, and what percentage of overall company sales does each top product generate?

```sql
WITH ProductSales AS (
    SELECT 
        p.stock_code,
        p.description,
        ROUND(SUM(f.line_total), 2) AS product_net_revenue,
        SUM(f.quantity) AS units_sold
    FROM fact_sales f
    INNER JOIN dim_product p ON f.stock_code = p.stock_code
    GROUP BY p.stock_code, p.description
)
SELECT 
    stock_code,
    description,
    units_sold,
    product_net_revenue,
    ROUND(product_net_revenue * 100.0 / (SELECT SUM(line_total) FROM fact_sales), 2) AS pct_of_total_revenue
FROM ProductSales
ORDER BY product_net_revenue DESC
LIMIT 5;
```
**Actual Result**:
1. `DOT` — **DOTCOM POSTAGE**: £206,245.48 (2.12% of total revenue)
2. `22423` — **REGENCY CAKESTAND 3 TIER**: £164,459.49 (1.69% of total revenue)
3. `85123A` — **WHITE HANGING HEART T-LIGHT HOLDER**: £99,790.93 (1.02% of total revenue)
4. `47566` — **PARTY BUNTING**: £98,289.14 (1.01% of total revenue)
5. `85099B` — **JUMBO BAG RED RETROSPOT**: £92,234.15 (0.95% of total revenue)

---

### Query 7: Average Order Value (AOV) by Market Region
**Business Question**: Do international export orders yield higher average order values than domestic UK purchases?

```sql
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
```
**Actual Result**:
- **International Export**: Completed Orders: **169** | Total Revenue: **£264,142.26** | **AOV: £1,562.97** | Avg Units/Order: **871.0**
- **European Union**: Completed Orders: **1,772** | Total Revenue: **£1,376,224.45** | **AOV: £776.65** | Avg Units/Order: **439.2**
- **Domestic UK**: Completed Orders: **18,019** | Total Revenue: **£9,001,744.09** | **AOV: £499.57** | Avg Units/Order: **257.9**

*Takeaway: International orders are over **3.1x larger** than UK orders, representing wholesale business-to-business (B2B) bulk purchasing.*

---

### Query 10: Repeat Customer Distribution & Retention
**Business Question**: What proportion of our registered customer accounts are one-time buyers versus repeat customers?

```sql
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
```
**Actual Result**:
| Loyalty Tier | Customer Count | Customer % | Revenue (£) | Revenue % |
| :--- | :---: | :---: | :---: | :---: |
| **2-5 Orders (Repeat Customer)** | 1,972 | 45.12% | £1,793,433.15 | 21.66% |
| **1 Order (One-Time Buyer)** | 1,312 | 30.02% | £431,608.86 | 5.21% |
| **6-10 Orders (Loyal Customer)** | 628 | 14.37% | £1,423,846.41 | 17.20% |
| **10+ Orders (VIP / Power Buyer)** | 459 | 10.50% | £4,629,630.99 | 55.92% |

*Takeaway: A classic Pareto phenomenon: the **top 10.5% of customers (VIP buyers with 10+ orders) generate 55.92% of total registered revenue**.*

---

### Query 13: Customer Revenue Ranking and Decile Segmentation
**Business Question**: How are registered customers segmented by decile (top 10%, next 10%), and what is the spend threshold for each tier?

```sql
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
WHERE revenue_rank <= 5
ORDER BY revenue_rank ASC;
```
**Actual Result**:
1. Rank 1: Customer `14646` (Netherlands) — 76 orders — **£279,489.02**
2. Rank 2: Customer `18102` (United Kingdom) — 62 orders — **£256,438.49**
3. Rank 3: Customer `17450` (United Kingdom) — 55 orders — **£187,322.17**
4. Rank 4: Customer `14911` (EIRE) — 248 orders — **£132,572.63**
5. Rank 5: Customer `12415` (Australia) — 26 orders — **£123,725.45**

---

### Query 14: Running Cumulative Revenue Throughout 2011
**Business Question**: How did revenue accumulate over time throughout 2011?

```sql
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
```
**Actual Result (Cumulative Trajectory)**:
- 2010-12: £746,723.61 -> Cumulative: **£746,723.61**
- 2011-03: £580,001.04 -> Cumulative: **£2,382,199.62**
- 2011-06: £691,123.36 -> Cumulative: **£4,286,638.79**
- 2011-09: £1,018,600.08 -> Cumulative: **£6,723,283.82**
- 2011-11: £1,461,756.24 -> Cumulative: **£9,235,595.63**
- 2011-12 (partial): £512,535.44 -> Final Net Total: **£9,748,131.07**
