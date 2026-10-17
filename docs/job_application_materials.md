# RetailPulse: Job Application & Interview Materials

This document provides ATS-friendly resume bullets, a LinkedIn portfolio post, interview talking points, and 10 technical interview Q&As tailored for **Data Analyst**, **Junior Data Analyst**, **BI Analyst**, and **SQL Developer** roles.

---

## 1. ATS-Friendly Resume Bullets

Copy and paste these bullet points directly into the **Projects** section of your resume:

- **RetailPulse — Sales & Customer Intelligence Analytics Platform** | *Python, SQLite, SQL, Power BI, DAX, pytest*
  - Engineered an end-to-end retail analytics data pipeline processing **541,909 raw transactions** into a normalized **Star Schema** (`fact_sales`, `dim_customer`, `dim_product`, `dim_date`, `dim_geography`), achieving 100% financial reconciliation across **£9.75M in net commercial revenue**.
  - Developed and automated an embedded **SQLite relational database** and authored **15 production analytical queries** utilizing CTEs, window functions (`NTILE`, `DENSE_RANK`, `SUM OVER`), and cohort analysis to identify that repeat buyers generate **94.79% of registered customer spend**.
  - Architected a **4-page Power BI executive dashboard blueprint** featuring single-direction star-schema relationships, Date table configuration, and **15+ custom DAX measures** (MoM/YoY growth, AOV, refund rate %, guest checkout revenue contribution), backed by a 15-test automated `pytest` quality suite.

---

## 2. Professional LinkedIn Project Post

Copy, paste, and customize this post for LinkedIn to showcase your project:

```text
🚀 Excited to share my latest end-to-end Data Analytics project: RetailPulse — Sales & Customer Intelligence Platform!

As aspiring data analysts, we often see tutorials that jump straight into dashboards without touching real data pipeline complexities. In this project, I wanted to mirror the complete enterprise analytics lifecycle from raw transactional messy data to executive decision-making.

Here is what I built:
🔹 Data Engineering & Cleaning (Python & Pandas): Ingested 541,909 raw e-commerce records from the UCI Machine Learning Repository. Audited 5,268 exact duplicates, isolated 2,512 non-commercial inventory write-offs, and classified 9,251 genuine customer returns ('C' invoices) while preserving £1.47M in guest checkout revenue.
🔹 Relational Star Schema (SQLite): Built an 83 MB relational database featuring FactSales and 4 Dimension tables (Customer, Product, Date, Geography) with foreign key constraints, B-Tree indexes, and zero orphan records.
🔹 Advanced SQL Analytics: Authored 15 production business queries demonstrating CTEs, Window Functions (NTILE decile segmentation, DENSE_RANK, running totals), and monthly cohort retention.
🔹 Business Intelligence (Power BI & DAX): Architected a 4-page dashboard blueprint (Executive Overview, Sales Performance, Customer Intelligence, Returns & Insights) powered by 15+ custom DAX measures for time intelligence and customer lifetime spend.
🔹 Automated Quality Assurance: Authored a 15-test pytest test suite ensuring 100% data integrity and financial reconciliation across £9.75M in net revenue.

💡 Key Business Discovery:
While the domestic UK market accounts for 84.0% of total revenue, international export orders average £1,562 per basket—over 3.1x larger than UK orders (£500)—revealing that overseas customers are high-value commercial wholesalers rather than casual consumers.

Check out the full repository, documentation, and SQL queries on GitHub:
👉 [Insert your GitHub Link]

Feedback and thoughts are welcome!

#DataAnalytics #PowerBI #SQL #Python #DataScience #BusinessIntelligence #PortfolioProject #JobSearch
```

---

## 3. Five Core Interview Talking Points

### Point 1: Why the Project Was Built
*"I built RetailPulse to demonstrate that I understand the full data analytics lifecycle—not just building pretty visuals in Power BI, but the hard engineering work that happens first. I wanted to take genuine, messy retail transactional data, build a defensible Star Schema relational database, write advanced analytical SQL queries, and present actionable insights that a VP of Sales or Operations Manager can actually use to make business decisions."*

### Point 2: Critical Data Cleaning Decisions
*"The most critical decision was how to treat negative quantities and missing values. Many beginners blindly drop negative numbers or nulls. By inspecting the data, I discovered that invoices starting with 'C' were legitimate customer returns, which I preserved to compute an 8.4% refund rate, while negative quantities without 'C' were internal warehouse stock adjustments where price was zero. Furthermore, 24.9% of transactions lacked a Customer ID because they were guest checkouts. Dropping them would have discarded £1.47M in revenue. Instead, I established a sentinel record (`customer_id = -1`) in `dim_customer`, preserving all sales without breaking foreign key referential integrity."*

### Point 3: Advanced SQL Techniques Used
*"In SQLite, I wrote 15 production queries covering CTEs, window functions, and cohort analysis. For example, in Query 13, I used `NTILE(10) OVER (ORDER BY total_spend DESC)` to segment customers into spending deciles, revealing that our top 10% of customers generate over 55% of total sales. In Query 14, I used `SUM(monthly_sales) OVER (ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` to generate cumulative running revenue totals across the year."*

### Point 4: Power BI Data Modeling & DAX Strategy
*"I avoided flat, wide tables and instead implemented a pure Star Schema with single-direction 1-to-many relationships from dimensions to facts. I marked the date table officially and configured column sort orders so that months sort chronologically rather than alphabetically. In DAX, I created a dedicated `_Measures` table housing 15+ formulas, including `PREVIOUSMONTH` and `SAMEPERIODLASTYEAR` for time intelligence, and safe `DIVIDE` functions to prevent division-by-zero errors."*

### Point 5: Business Insight & Future Improvement
*"One of the most interesting findings was the international wholesale basket multiplier. Although the UK accounts for 84% of revenue, international export orders average £1,562 compared to £500 in the UK. International buyers are bulk wholesalers. However, distant markets like Singapore and Hong Kong suffer from return rates exceeding 35%. My strategic recommendation was to overhaul export packaging and transit insurance. As a future improvement, I would incorporate product acquisition cost data (COGS) to calculate true gross margins, since the raw public dataset only contains selling prices."*

---

## 4. Ten Likely Interview Questions & Model Answers

### Q1: What is the difference between a Star Schema and a normalized 3NF schema, and why did you choose Star Schema for RetailPulse?
**Model Answer**:  
*"A 3NF (Third Normal Form) schema is optimized for OLTP (transactional writing) by eliminating data redundancy through normalization. A Star Schema, by contrast, is optimized for OLAP (analytical querying and reporting). It places a centralized Fact table containing additive numerical metrics (`line_total`, `quantity`) surrounded by de-normalized Dimension tables (`Customer`, `Product`, `Date`, `Geography`). I chose a Star Schema because it drastically reduces the number of joins needed, eliminates circular filter dependencies in Power BI, and allows the VertiPaq columnar engine to scan columns with maximum compression."*

---

### Q2: Why did you keep customer cancellations in the Fact table instead of deleting them?
**Model Answer**:  
*"In retail accounting, customer returns and cancellations are genuine business events, not data entry errors. If you delete them, you artificially inflate your revenue and blind management to product defects or refund friction. By preserving returns with an `is_return = 1` flag and negative `line_total`, our database accurately calculates both Gross Sales (£10.64M) and Net Revenue (£9.75M), while allowing us to calculate an exact Return Rate of 8.40%."*

---

### Q3: How did you handle the 24.9% of transactions with missing Customer IDs?
**Model Answer**:  
*"In e-commerce, missing customer IDs usually represent unauthenticated guest checkouts. Deleting these 132,565 rows would have erased £1,469,611.65 (15.08%) in genuine sales. To maintain strict relational foreign key integrity, I assigned guest transactions a foreign key of `customer_id = -1` in `fact_sales` and inserted a matching sentinel row in `dim_customer` with `customer_type = 'Guest Checkout'`. In DAX and SQL, I explicitly filter for `customer_id <> -1` when analyzing retention or repeat purchase rates, but include all rows when reporting total revenue."*

---

### Q4: Explain how you implemented Month-over-Month (MoM) growth in DAX.
**Model Answer**:  
*"First, I ensured that `dim_date` was marked as an official Date Table on `order_date`. Then, I created a base measure `[Net Revenue] = SUM(fact_sales[line_total])`. Next, I created `[Previous Month Net Sales] = CALCULATE([Net Revenue], PREVIOUSMONTH(dim_date[order_date]))`. Finally, I computed `[MoM Growth %] = DIVIDE([Net Revenue] - [Previous Month Net Sales], [Previous Month Net Sales], 0)`. Using `DIVIDE` guarantees that if the prior month is blank or zero, Power BI displays a clean blank or zero rather than an unsightly `#VALUE!` or `#DIV/0!` error."*

---

### Q5: How did you test and validate that your data was clean and accurate?
**Model Answer**:  
*"I implemented a 15-test automated `pytest` test suite in `tests/`. It programmatically verifies that:
1. Sales row counts (524,878) plus Return row counts (9,251) equal Cleaned row counts (534,129).
2. Gross Sales (£10.64M) plus Returns (-£0.89M) reconcile to Net Revenue (£9.75M) with zero variance.
3. 100% of foreign keys in `fact_sales` resolve to existing primary keys in dimension tables with zero orphan records.
4. There are zero exact duplicate rows in the cleaned dataset.
This guarantees that any changes to our cleaning scripts can be tested automatically for regression."*

---

### Q6: What SQL window functions did you use and what business questions did they answer?
**Model Answer**:  
*"I utilized several window functions in `sql/analysis_queries.sql`:
- `NTILE(10) OVER (ORDER BY total_spend DESC)`: Divided registered customers into 10 equal decile buckets to evaluate wealth concentration.
- `DENSE_RANK() OVER (ORDER BY total_spend DESC)`: Ranked customers by lifetime spend without skipping ranks.
- `SUM(monthly_sales) OVER (ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`: Computed cumulative running revenue throughout 2011 to track pace toward annual revenue targets.
- `SUM(line_total) * 100.0 / SUM(SUM(line_total)) OVER ()`: Calculated each product's percentage contribution to total business revenue inside a single query."*

---

### Q7: Why did you exclude records with UnitPrice <= 0?
**Model Answer**:  
*"When profiling the dataset, I found 2,512 rows with `UnitPrice <= 0`. Cross-tabulating these records revealed that 1,336 were negative-quantity records with descriptions like 'Damaged', 'lost', and 'check', and 2 were 'Adjust bad debt' corrections. These represent internal warehouse inventory adjustments and accounting write-offs, not transactions with paying customers. Leaving them in would distort customer basket sizes and pricing distributions. Filtering `UnitPrice > 0` cleanly removed internal accounting artifacts while preserving 100% of valid customer sales and returns."*

---

### Q8: What was your most surprising finding from the data?
**Model Answer**:  
*"The sharp dichotomy between domestic UK and international export basket sizes. Domestic UK orders averaged £499.57 per order, whereas international export orders averaged £1,562.97—over 3.1 times larger. Furthermore, international orders averaged 871 units per basket compared to 258 units in the UK. This indicates that international marketing should not target individual retail shoppers, but rather commercial wholesalers and distributors who buy in bulk to amortize international freight costs."*

---

### Q9: Did you calculate profit or profit margins for this company? Why or why not?
**Model Answer**:  
*"No, I deliberately did not calculate profit or profit margin because the genuine UCI Online Retail dataset contains retail selling prices but no product cost data (COGS). A common mistake among junior analysts is to assume an arbitrary cost (like 60% of price) and present it as 'profit'. As a data analyst, data integrity is paramount: you must never fabricate assumptions and present them as historical facts. I clearly documented that all financial metrics represent Gross Sales, Refunds, and Net Revenue."*

---

### Q10: How would you scale this project if the company grew from 500k rows to 500 million rows?
**Model Answer**:  
*"At 500 million rows, an embedded SQLite database and flat CSV files would hit memory and I/O bottlenecks. I would scale the architecture by:
1. Ingestion: Moving from batch CSV downloads to an event streaming or incremental batch tool like Apache Airflow or Azure Data Factory.
2. Data Lakehouse: Storing raw transactional logs in Delta Lake / Parquet format on cloud object storage (e.g., Azure ADLS Gen2 or AWS S3).
3. Cloud Data Warehouse: Loading into a cloud warehouse like Snowflake, BigQuery, or Databricks with partitioned tables on `date_key`.
4. Power BI Storage Mode: Switching from full Import Mode to DirectLake (in Microsoft Fabric) or a Composite Model with aggregations, where summary metrics are cached in VertiPaq memory and granular line-item drill-throughs query the warehouse directly."*
