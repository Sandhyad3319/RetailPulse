"""
RetailPulse: Data Validation & Quality Assurance Script
=======================================================
Validates the processed dataset files and Star Schema dimensions against
rigorous data quality rules, schema constraints, and financial reconciliation.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def validate_pipeline_outputs():
    print("=" * 68)
    print(" RetailPulse: Automated Data Quality & Integrity Validation ")
    print("=" * 68)

    errors = []
    warnings = []

    # 1. Check file existence
    expected_files = [
        "cleaned_transactions.csv",
        "sales_transactions.csv",
        "returns_cancellations.csv",
        "fact_sales.csv",
        "dim_customer.csv",
        "dim_product.csv",
        "dim_date.csv",
        "dim_geography.csv",
        "data_quality_report.csv"
    ]
    print("\n[1/6] Verifying processed file existence...")
    for f in expected_files:
        file_path = PROCESSED_DIR / f
        if file_path.exists() and file_path.stat().st_size > 0:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"    [OK] {f:<26} ({size_mb:5.2f} MB)")
        else:
            errors.append(f"Missing or empty expected output file: {f}")
            print(f"    [FAIL] {f:<26} MISSING")

    if errors:
        print("\n[-] Validation aborted due to missing files.")
        return False, errors, warnings

    # Load dataframes for testing
    print("\n[2/6] Loading processed datasets for rule validation...")
    df_clean = pd.read_csv(PROCESSED_DIR / "cleaned_transactions.csv", low_memory=False)
    df_sales = pd.read_csv(PROCESSED_DIR / "sales_transactions.csv", low_memory=False)
    df_returns = pd.read_csv(PROCESSED_DIR / "returns_cancellations.csv", low_memory=False)
    df_fact = pd.read_csv(PROCESSED_DIR / "fact_sales.csv", low_memory=False)
    df_cust = pd.read_csv(PROCESSED_DIR / "dim_customer.csv", low_memory=False)
    df_prod = pd.read_csv(PROCESSED_DIR / "dim_product.csv", low_memory=False)
    df_date = pd.read_csv(PROCESSED_DIR / "dim_date.csv", low_memory=False)
    df_geo = pd.read_csv(PROCESSED_DIR / "dim_geography.csv", low_memory=False)

    # 2. Row count reconciliation
    print("\n[3/6] Auditing row count integrity and segmentation...")
    clean_count = len(df_clean)
    sales_count = len(df_sales)
    returns_count = len(df_returns)
    fact_count = len(df_fact)

    print(f"    Cleaned Transactions: {clean_count:,}")
    print(f"    Sales Transactions:   {sales_count:,}")
    print(f"    Return Transactions:  {returns_count:,}")
    print(f"    Fact Sales Records:   {fact_count:,}")

    if sales_count + returns_count != clean_count:
        errors.append(f"Row count mismatch: Sales ({sales_count:,}) + Returns ({returns_count:,}) != Cleaned ({clean_count:,})")
    else:
        print("    [PASS] Sales + Returns exactly equals Cleaned Transactions total.")

    if fact_count != clean_count:
        errors.append(f"Fact table row count ({fact_count:,}) does not match Cleaned Transactions ({clean_count:,})")
    else:
        print("    [PASS] Fact table row count matches Cleaned Transactions exactly.")

    # 3. Financial Reconciliation
    print("\n[4/6] Auditing financial reconciliation (Gross + Returns == Net)...")
    sales_val = df_sales["line_total"].sum()
    returns_val = df_returns["line_total"].sum()
    clean_val = df_clean["line_total"].sum()
    fact_val = df_fact["line_total"].sum()

    print(f"    Gross Sales Value:  £{sales_val:,.2f}")
    print(f"    Return/Refund Value: £{returns_val:,.2f}")
    print(f"    Net Cleaned Value:  £{clean_val:,.2f}")
    print(f"    Net Fact Table Val: £{fact_val:,.2f}")

    diff_clean = abs((sales_val + returns_val) - clean_val)
    diff_fact = abs(clean_val - fact_val)

    if diff_clean > 0.05:
        errors.append(f"Financial reconciliation failed: Gross ({sales_val:.2f}) + Return ({returns_val:.2f}) != Net ({clean_val:.2f}), Diff: {diff_clean:.4f}")
    else:
        print(f"    [PASS] Sales + Returns reconciles to Net Revenue (Variance: £{diff_clean:.2f}).")

    if diff_fact > 0.05:
        errors.append(f"Fact table financial total (£{fact_val:.2f}) differs from Cleaned table (£{clean_val:.2f})")
    else:
        print("    [PASS] Fact table revenue reconciles to Cleaned table revenue.")

    # 4. Classification & Constraint Rules
    print("\n[5/6] Auditing business rules and column constraints...")

    # Rule A: All returns must have negative quantity and 'C' invoice
    invalid_returns_qty = df_returns[df_returns["quantity"] >= 0]
    invalid_returns_code = df_returns[~df_returns["invoice_no"].astype(str).str.startswith(("C", "c"))]
    if len(invalid_returns_qty) > 0:
        errors.append(f"Found {len(invalid_returns_qty)} return records with non-negative quantity.")
    else:
        print("    [PASS] 100% of return records have negative quantities.")

    if len(invalid_returns_code) > 0:
        errors.append(f"Found {len(invalid_returns_code)} return records without 'C' invoice prefix.")
    else:
        print("    [PASS] 100% of return records have 'C' invoice prefix.")

    # Rule B: All sales must have positive quantity and positive unit price
    invalid_sales_qty = df_sales[df_sales["quantity"] <= 0]
    invalid_sales_price = df_sales[df_sales["unit_price"] <= 0]
    if len(invalid_sales_qty) > 0:
        errors.append(f"Found {len(invalid_sales_qty)} sales records with non-positive quantity.")
    else:
        print("    [PASS] 100% of sales records have strictly positive quantity.")

    if len(invalid_sales_price) > 0:
        errors.append(f"Found {len(invalid_sales_price)} sales records with non-positive unit price.")
    else:
        print("    [PASS] 100% of sales records have strictly positive unit price.")

    # Rule C: Exact duplicates in cleaned table
    clean_dups = df_clean.duplicated().sum()
    if clean_dups > 0:
        errors.append(f"Found {clean_dups} duplicate rows in cleaned_transactions.csv.")
    else:
        print("    [PASS] Zero exact duplicate rows present in cleaned dataset.")

    # 5. Referential Integrity (Star Schema Key Integrity)
    print("\n[6/6] Auditing Star Schema referential key integrity...")

    # A: Customer foreign key
    orphan_cust = set(df_fact["customer_id"]) - set(df_cust["customer_id"])
    if orphan_cust:
        errors.append(f"Found {len(orphan_cust)} orphan customer IDs in Fact table.")
    else:
        print("    [PASS] 100% of Fact customer_ids exist in DimCustomer.")

    # B: Product foreign key
    orphan_prod = set(df_fact["stock_code"]) - set(df_prod["stock_code"])
    if orphan_prod:
        errors.append(f"Found {len(orphan_prod)} orphan stock codes in Fact table.")
    else:
        print("    [PASS] 100% of Fact stock_codes exist in DimProduct.")

    # C: Date foreign key
    orphan_date = set(df_fact["date_key"]) - set(df_date["date_key"])
    if orphan_date:
        errors.append(f"Found {len(orphan_date)} orphan date keys in Fact table.")
    else:
        print("    [PASS] 100% of Fact date_keys exist in DimDate.")

    # D: Geography foreign key
    orphan_geo = set(df_fact["country_key"]) - set(df_geo["country_key"])
    if orphan_geo:
        errors.append(f"Found {len(orphan_geo)} orphan country keys in Fact table.")
    else:
        print("    [PASS] 100% of Fact country_keys exist in DimGeography.")

    # Final Summary
    print("\n" + "=" * 68)
    if errors:
        print(" [-] VALIDATION FAILED WITH ERRORS:")
        for err in errors:
            print(f"     * {err}")
        print("=" * 68)
        return False, errors, warnings
    else:
        print(" [+] ALL VALIDATION AUDITS PASSED WITH ZERO ERRORS!")
        print(f"     Total Valid Commercial Records: {clean_count:,}")
        print(f"     Total Net Revenue Reconciled:   £{clean_val:,.2f}")
        print("=" * 68)
        return True, errors, warnings


if __name__ == "__main__":
    success, errs, warns = validate_pipeline_outputs()
    if not success:
        sys.exit(1)
