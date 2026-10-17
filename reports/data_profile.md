# RetailPulse: Dataset Profiling & Data Understanding Report

**Generated Date**: 2026-10-17 16:28:06  
**Source Dataset**: UCI Machine Learning Repository — Online Retail  
**File Inspected**: `Online Retail.xlsx` (22.62 MB)  
**Permanent Raw Path**: `data/raw/Online Retail.xlsx`  

---

## 1. Executive Summary & Key Dataset Dimensions

| Metric | Value | Business Interpretation |
| :--- | :--- | :--- |
| **Total Transaction Records (Rows)** | **541,909** | Individual line-item records across all orders |
| **Total Features (Columns)** | **8** | Standard e-commerce transaction schema |
| **Date Range** | **2010-12-01 08:26:00 to 2011-12-09 12:50:00** | 1 year and 9 days of transactional history |
| **Unique Invoices** | **25,900** | Distinct order transactions (including cancellations) |
| **Unique Products (StockCodes)** | **4,070** | Distinct SKU identifiers |
| **Unique Product Descriptions** | **4,223** | Text descriptions (note: exceeds StockCode count due to variations) |
| **Unique Customer IDs** | **4,372** | Registered customer accounts |
| **Unique Countries** | **38** | Geographic footprint across Europe and international markets |
| **Exact Duplicate Rows** | **5,268 (0.97%)** | Identical repeated line items requiring deduplication review |

---

## 2. Column Schema & Data Quality Audit

| Column Name | Raw Data Type | Missing Count | Missing % | Unique Values | Sample Value | Data Quality Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `InvoiceNo` | `object` | 0 | 0.00% | 25,900 | `536365` | Alphanumeric code; prefixes like 'C' denote cancellations |
| `StockCode` | `object` | 0 | 0.00% | 4,070 | `85123A` | Clean |
| `Description` | `object` | 1,454 | 0.27% | 4,223 | `WHITE HANGING HEART T-LIGHT HO` | Missing in 1,454 rows; often correlates with inventory adjustments |
| `Quantity` | `int64` | 0 | 0.00% | 722 | `6` | Includes negative values denoting returned/cancelled items |
| `InvoiceDate` | `datetime64[us]` | 0 | 0.00% | 23,260 | `2010-12-01 08:26:00` | Clean |
| `UnitPrice` | `float64` | 0 | 0.00% | 1,630 | `2.55` | Includes 0.00 entries (promotions/adjustments) and rare negative adjustments |
| `CustomerID` | `float64` | 135,080 | 24.93% | 4,372 | `17850.0` | High missing rate (24.93%) representing unregistered/guest purchases |
| `Country` | `str` | 0 | 0.00% | 38 | `United Kingdom` | Clean |

---

## 3. Investigation of Cancellations, Returns & Negative Values

In retail transactional systems, negative values are not automatically random errors—they frequently convey critical business operations: returns, order voids, discounts, damages, and bad debt adjustments.

### Key Finding 1: Cancellation Invoices ('C' Prefix)
- **Total Invoices starting with 'C' / 'c'**: **9,288 rows** (1.71% of all records).
- **Invoices with 'C' AND negative Quantity**: **9,288 rows** (100% of 'C' invoices have negative quantities).
- **Invoices with 'C' AND positive Quantity**: **0 rows**.

### Key Finding 2: Negative Quantities Without 'C' Prefix
- **Negative quantity rows without 'C' prefix**: **1,336 rows**.
- **Nature of these records**: Inspection reveals these are system inventory adjustments, damaged items, write-offs, or stocktaking entries (e.g., Description = *"Damaged"*, *"lost"*, *"check"*, *"wrongly marked"*).
- **Customer ID Presence**: Almost 100% of negative quantity rows without 'C' have `CustomerID = NaN` and `UnitPrice = 0.00`. They represent internal operational accounting, not customer transactions.

### Key Finding 3: Price Anomalies
- **Rows with UnitPrice < 0**: **2 rows** (e.g., Debt adjustments like `"Adjust bad debt"`).
- **Rows with UnitPrice == 0**: **2,515 rows** (Free gift giveaways, sample items, or inventory void logs).
- **Rows with UnitPrice > 0**: **539,392 rows** (99.54%).

---

## 4. Customer ID Missingness Analysis (Registered vs. Guest Checkout)

| Customer ID Category | Row Count | Percentage | Business Meaning |
| :--- | :--- | :--- | :--- |
| **Known Customer ID** | **406,829** | **75.07%** | Registered loyalty / repeat account purchases |
| **Missing Customer ID (`NaN`)** | **135,080** | **24.93%** | Guest checkouts, telephone orders, or unauthenticated baskets |

> [!IMPORTANT]
> **Data Cleaning Rule**: We must **not blindly drop** missing Customer ID rows when computing **Total Sales Volume** or **Product Sales Rankings**, because guest customers contribute real corporate revenue. However, for **Customer Intelligence & Retention Analysis** (Page 3 of dashboard), we must isolate the registered cohort where `CustomerID` is present.

---

## 5. Statistical Distribution Summary

### Quantity Summary
- **Minimum**: `-80,995` (Maximum single cancellation)
- **25th Percentile (Q1)**: `1`
- **Median (50%)**: `3`
- **Mean**: `9.55`
- **75th Percentile (Q3)**: `10`
- **Maximum**: `80,995` (Wholesale bulk purchase)

### Unit Price Summary (in GBP / Sterling £)
- **Minimum**: `£-11,062.06`
- **25th Percentile (Q1)**: `£1.25`
- **Median (50%)**: `£2.08`
- **Mean**: `£4.61`
- **75th Percentile (Q3)**: `£4.13`
- **Maximum**: `£38,970.00`

---

## 6. Geographic Distribution (Top 10 Markets)

| Rank | Country | Transaction Rows | % of Total Transactions |
| :---: | :--- | :--- | :--- |
| 1 | **United Kingdom** | 495,478 | 91.43% |
| 2 | **Germany** | 9,495 | 1.75% |
| 3 | **France** | 8,557 | 1.58% |
| 4 | **EIRE** | 8,196 | 1.51% |
| 5 | **Spain** | 2,533 | 0.47% |
| 6 | **Netherlands** | 2,371 | 0.44% |
| 7 | **Belgium** | 2,069 | 0.38% |
| 8 | **Switzerland** | 2,002 | 0.37% |
| 9 | **Portugal** | 1,519 | 0.28% |
| 10 | **Australia** | 1,259 | 0.23% |

*Note: The **United Kingdom** accounts for **91.4%** of all transactional records, making this a heavily domestic UK retail business with international wholesale exports.*

---

## 7. Data Cleaning Strategy for Phase 3

Based on our empirical findings, our cleaning pipeline (`clean_data.py`) will implement these documented rules:
1. **Deduplication**: Remove exact duplicate rows (5,268 rows) caused by web logging double-clicks.
2. **Cancellations & Returns Flagging**:
   - Create an explicit boolean flag `IsReturn` (`True` if `InvoiceNo` starts with 'C').
   - Keep customer returns in `FactSales` with negative revenue contribution to accurately report both **Gross Sales** and **Net Sales**.
3. **Internal Accounting Exclusions**:
   - Filter out operational adjustment records (where `UnitPrice == 0` AND `CustomerID IS NULL` AND description contains adjustment keywords).
4. **Date & Calendar Feature Engineering**:
   - Cast `InvoiceDate` to proper datetime format.
   - Extract `OrderDate`, `Year`, `Quarter`, `Month`, `MonthName`, `DayOfWeek`, and `Hour`.
5. **Star Schema Generation**:
   - Generate normalized dimension tables (`DimCustomer`, `DimProduct`, `DimDate`, `DimGeography`) and fact table (`FactSales`) for SQLite and Power BI.
