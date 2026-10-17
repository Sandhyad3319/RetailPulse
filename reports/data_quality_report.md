# RetailPulse: Data Quality & Integrity Report

**Report Date**: 2026-10-17  
**Validation Suite**: `python/validate_data.py` & `tests/test_data_quality.py`  
**Overall Status**: **PASSED (8/8 Tests Passed - 100% Integrity)**  

---

## 1. Executive Quality Audit & Traceability

This report documents the automated quality audits and reconciliation checks performed on the cleaned **RetailPulse** datasets and dimensional tables.

### End-to-End Pipeline Reconciliation

| Metric / Dimension | Raw Value | Cleaned Value | Delta / Excluded | Methodological Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **Total Transaction Records** | **541,909** | **534,129** | **-7,780 (-1.44%)** | 5,268 exact duplicates + 2,512 administrative adjustments removed |
| **Gross Commercial Sales Rows** | N/A | **524,878** | N/A | Valid orders where `Quantity > 0` and `UnitPrice > 0` |
| **Returns / Cancellation Rows** | N/A | **9,251** | N/A | Valid returns where `Quantity < 0` and `InvoiceNo` starts with `'C'` |
| **Gross Sales Value (£)** | N/A | **£10,642,110.80** | N/A | Revenue generated prior to refund deductions |
| **Customer Returns Value (£)** | N/A | **-£893,979.73** | N/A | Total financial refund stream |
| **Net Commercial Revenue (£)** | N/A | **£9,748,131.07** | N/A | Gross Sales + Return Total (Exact zero-variance match) |
| **Registered Customer Accounts** | 4,372 | **4,371** | -1 | 1 account had only administrative negative adjustment entries |
| **Distinct Product SKUs** | 4,070 | **3,828** | -242 | 242 administrative codes (e.g., `B` bad debt, warehouse write-offs) |
| **Distinct Calendar Dates** | 305 | **305** | 0 | 100% of calendar dates preserved (Dec 1, 2010 to Dec 9, 2011) |
| **Countries Represented** | 38 | **38** | 0 | 100% of geographic markets preserved |

---

## 2. Automated Test Results (`pytest tests/test_data_quality.py`)

All automated integration tests executed against the generated files in `data/processed/` passed with zero errors:

| Test Case | Description | Result | Details |
| :--- | :--- | :---: | :--- |
| `test_processed_files_exist` | Confirms all 9 required processed CSV files exist on disk | **PASSED** | All files present and non-empty |
| `test_row_count_integrity` | Verifies `Sales (524,878) + Returns (9,251) == Cleaned (534,129)` | **PASSED** | Exact match |
| `test_financial_reconciliation` | Verifies `Gross (£10.64M) + Returns (-£0.89M) == Net (£9.75M)` | **PASSED** | Exact zero-penny variance |
| `test_cancellation_and_return_classification` | Verifies 100% of returns have `Quantity < 0` and `'C'` invoice code | **PASSED** | 9,251 / 9,251 compliant |
| `test_sales_classification` | Verifies 100% of sales have `Quantity > 0` and `UnitPrice > 0` | **PASSED** | 524,878 / 524,878 compliant |
| `test_no_exact_duplicates_in_cleaned` | Audits cleaned dataset for accidental duplicate retention | **PASSED** | 0 duplicate rows detected |
| `test_star_schema_referential_integrity` | Verifies 0 orphan foreign keys from FactSales to all Dimensions | **PASSED** | 100% referential integrity |
| `test_date_range_bounds` | Confirms all dates fall between 2010-12-01 and 2011-12-31 | **PASSED** | No corrupted date stamps |

---

## 3. Star Schema Relational Validation

The dimensional model generated in `data/processed/` complies with relational database best practices:

```text
FactSales (534,129 rows)
├── FK: customer_id  --> DimCustomer (4,372 rows: 4,371 registered + 1 guest) [0 Orphan Keys]
├── FK: stock_code   --> DimProduct (3,828 distinct SKUs)                     [0 Orphan Keys]
├── FK: date_key     --> DimDate (305 unique active trading dates)            [0 Orphan Keys]
└── FK: country_key  --> DimGeography (38 unique countries)                   [0 Orphan Keys]
```

### Guest Checkout Representation
To avoid losing £1.4+ million in guest checkout revenue while strictly maintaining foreign key constraints:
- Guest transactions in `fact_sales.csv` are assigned `customer_id = -1`.
- A matching record exists in `dim_customer.csv`:
  - `customer_id`: `-1`
  - `customer_type`: `Guest Checkout`
  - `country`: `Multiple`
  - `total_orders`: `1,624` distinct guest invoices
  - `total_spend`: `£1,446,552.12`

---

## 4. Unresolved Limitations & Governance Notes

1. **Lack of Cost of Goods Sold (COGS)**:
   - The raw dataset does not contain supplier acquisition costs or product wholesale margins.
   - Profit and margin calculations will not be fabricated in SQL or DAX. The analysis strictly adheres to **Gross Sales**, **Refund Value**, and **Net Revenue**.
2. **Missing Product Descriptions in Raw Data**:
   - 1,454 rows had missing descriptions in the raw dataset. Most corresponded to inventory adjustments. The remaining valid commercial rows were assigned `"UNKNOWN DESCRIPTION"` to prevent null pointer exceptions in SQL and Power BI visuals.
3. **Truncated Final Month (Dec 2011)**:
   - The dataset ends on December 9, 2011. Analysts and business stakeholders must note that December 2011 represents only 9 days of trading, making month-over-month comparisons for Dec 2011 non-representative without daily normalization.
