# RetailPulse: Final Quality Assurance & Verification Report

**Audit Date**: 2026-10-17  
**Project**: RetailPulse — Sales & Customer Intelligence Analytics Platform  
**Audit Status**: **PASSED (15/15 Automated Integration Tests Passed — 100% Verified)**  
**Environment**: Windows 11 Pro, Python 3.12.10, SQLite 3, Power BI Desktop (Store Edition)  

---

## 1. Scope of Audit & Checks Performed

The full data lifecycle was audited across all six core dimensions:

1. **Dataset Acquisition & Attribution**: Verified download of original UCI Online Retail dataset (541,909 rows, 22.62 MB). Citation, license (CC BY 4.0), and donor documented.
2. **Data Cleaning & Preprocessing**: Audited deduplication (5,268 exact duplicates removed) and administrative exclusions (2,512 zero/negative price write-offs removed).
3. **Financial & Record Reconciliation**: Audited that `Gross Sales (£10,642,110.80) + Returns (-£893,979.73) == Net Commercial Revenue (£9,748,131.07)` across all CSVs and SQLite tables.
4. **Relational Star Schema & SQL Database**: Verified SQLite database (`data/processed/retailpulse.db`, 83.60 MB), table constraints, primary key uniqueness, foreign key relationships, and all 15 production business queries.
5. **Power BI Specifications & DAX Measures**: Audited Star Schema data model, 1-to-many single-direction relationships, Date table marking, and 15+ validated DAX formulas.
6. **Code Quality & Portability**: Verified zero hard-coded machine paths in Python and test files. Audited `.gitignore` to prevent raw data or credential leaks.

---

## 2. Actual Automated Test Results (`pytest tests/ -v`)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\USER\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Documents\RetailPulse
collecting ... collected 15 items

tests/test_data_quality.py::test_processed_files_exist PASSED            [  6%]
tests/test_data_quality.py::test_row_count_integrity PASSED              [ 13%]
tests/test_data_quality.py::test_financial_reconciliation PASSED         [ 20%]
tests/test_data_quality.py::test_cancellation_and_return_classification PASSED [ 26%]
tests/test_data_quality.py::test_sales_classification PASSED             [ 33%]
tests/test_data_quality.py::test_no_exact_duplicates_in_cleaned PASSED   [ 40%]
tests/test_data_quality.py::test_star_schema_referential_integrity PASSED [ 46%]
tests/test_data_quality.py::test_date_range_bounds PASSED                [ 53%]
tests/test_sql_database.py::test_database_tables_exist PASSED            [ 60%]
tests/test_sql_database.py::test_database_row_counts_match_csvs PASSED   [ 66%]
tests/test_sql_database.py::test_financial_reconciliation_in_sql PASSED  [ 73%]
tests/test_sql_database.py::test_foreign_key_integrity PASSED            [ 80%]
tests/test_sql_database.py::test_primary_key_uniqueness PASSED           [ 86%]
tests/test_sql_database.py::test_guest_checkout_representation PASSED    [ 93%]
tests/test_sql_database.py::test_all_15_queries_execute PASSED           [100%]

============================= 15 passed in 13.66s =============================
```

---

## 3. Issues Identified & Fixes Implemented

| Issue Discovered | Root Cause | Engineering Solution Implemented | Verification |
| :--- | :--- | :--- | :---: |
| **Windows App Execution Alias Interception** | Default Windows 10/11 shortcut intercepted `python` commands | Provided PATH configuration guidance and updated `check_env.ps1` to resolve user path dynamically | Passed |
| **PowerShell Unicode Encoding in Diagnostics** | Em-dash and unquoted ampersands in diagnostic script caused PowerShell parser error | Sanitized `check_env.ps1` with safe ASCII strings and explicit process environment path merging | Passed |
| **Missing Content-Length in UCI Header** | UCI web server streams chunked gzip without `Content-Length` | Refactored `python/download_data.py` to stream buffers with dynamic downloaded byte counter | Passed |
| **Guest Checkout Foreign Key Orphans** | 132,565 transactions (24.8%) lacked a customer ID | Assigned `customer_id = -1` in `fact_sales` and created a matching sentinel profile in `dim_customer` | Passed (0 orphan keys) |
| **Ambiguous Negative Quantities** | 1,336 negative quantity rows had no 'C' code | Diagnosed as internal warehouse write-offs (`UnitPrice == 0`); isolated from commercial sales | Passed |

---

## 4. Remaining Limitations & Manual Steps

1. **No Product Acquisition Cost (COGS)**:
   - The UCI dataset contains selling prices only. Profit, gross margin, and net margin cannot be calculated without fabricating costs. We strictly report **Gross Sales, Return Value, and Net Revenue**.
2. **Power BI Desktop Report Assembly**:
   - Power BI `.pbix` files require desktop UI compilation. We have provided click-by-click instructions in [README_POWERBI.md](file:///c:/Users/USER/Documents/RetailPulse/powerbi/README_POWERBI.md) so the user can assemble and save the finished file in ~15 minutes.
3. **Truncated December 2011**:
   - Transactions conclude on December 9, 2011 (9 active days), meaning December 2011 represents partial-month data.

---

## 5. Exact Commands to Reproduce Project from Scratch

To reproduce the entire data pipeline, database creation, and query export:

```powershell
# 1. Navigate to project root
cd c:\Users\USER\Documents\RetailPulse

# 2. Check environment readiness
powershell -ExecutionPolicy Bypass -File .\check_env.ps1

# 3. Download and extract raw UCI dataset
python python/download_data.py

# 4. Profile raw dataset
python python/profile_data.py

# 5. Clean data and generate Star Schema CSVs
python python/clean_data.py

# 6. Validate processed files
python python/validate_data.py

# 7. Create SQLite database and load tables
python python/load_sqlite.py

# 8. Execute all 15 SQL analytical queries
python python/run_sql_analysis.py

# 9. Run automated test suite
pytest tests/ -v
```
