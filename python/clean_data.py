"""
RetailPulse: Data Cleaning & Preprocessing Pipeline
===================================================
Cleans and transforms raw retail transaction records into an analysis-ready
commercial dataset and structured Star Schema tables for SQL and Power BI.

Pipeline Operations:
1. Deduplication: Eliminates exact duplicate records caused by web logging retries.
2. Administrative Filter: Excludes non-commercial internal records (UnitPrice <= 0,
   such as inventory write-offs, damaged stock notes, and bad debt adjustments).
3. Commercial Segmentation: Explicitly separates and flags:
   - Sales Transactions (Quantity > 0, UnitPrice > 0)
   - Customer Returns & Cancellations (Quantity < 0, UnitPrice > 0, 'C' invoice prefix)
4. Feature Engineering:
   - line_total = quantity * unit_price (preserves negative sign for returns)
   - order_date, date_key, year, quarter, month, month_name, day_of_week, hour
   - is_return, is_guest flags
5. Star Schema Generation:
   - FactSales, DimCustomer, DimProduct, DimDate, DimGeography
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXCEL_PATH = RAW_DIR / "Online Retail.xlsx"


def print_step(step_num: int, title: str):
    print(f"\n[{step_num}/6] {title}...")


def clean_retail_data():
    print("=" * 68)
    print(" RetailPulse: Data Cleaning & Star Schema Preprocessing Pipeline ")
    print("=" * 68)

    if not EXCEL_PATH.exists():
        print(f"[-] ERROR: Raw source file not found at: {EXCEL_PATH}")
        sys.exit(1)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print_step(1, "Loading raw Excel dataset")
    df_raw = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    raw_count = len(df_raw)
    print(f"    Raw records loaded: {raw_count:,} rows across {df_raw.shape[1]} columns")

    # Standardize Column Names
    rename_map = {
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country"
    }
    df = df_raw.rename(columns=rename_map)

    # 2. Deduplication
    print_step(2, "Auditing and removing exact duplicates")
    exact_dups = df.duplicated().sum()
    df_dedup = df.drop_duplicates().copy()
    print(f"    Exact duplicate rows removed: {exact_dups:,} ({exact_dups / raw_count * 100:.2f}%)")
    print(f"    Remaining rows after deduplication: {len(df_dedup):,}")

    # 3. Clean Strings and Data Types
    print_step(3, "Standardizing types and text fields")
    df_dedup["invoice_no"] = df_dedup["invoice_no"].astype(str).str.strip()
    df_dedup["stock_code"] = df_dedup["stock_code"].astype(str).str.strip().str.upper()
    df_dedup["description"] = df_dedup["description"].astype(str).str.strip()
    df_dedup.loc[df_dedup["description"] == "nan", "description"] = "UNKNOWN DESCRIPTION"
    df_dedup["country"] = df_dedup["country"].astype(str).str.strip()

    # Dates and Numerics
    df_dedup["invoice_date"] = pd.to_datetime(df_dedup["invoice_date"], errors="coerce")
    df_dedup["quantity"] = pd.to_numeric(df_dedup["quantity"], errors="coerce").fillna(0).astype(int)
    df_dedup["unit_price"] = pd.to_numeric(df_dedup["unit_price"], errors="coerce").fillna(0.0).astype(float)

    # Customer ID: keep null for guest, but use integer representation
    df_dedup["is_guest"] = df_dedup["customer_id"].isnull()
    df_dedup["customer_id"] = df_dedup["customer_id"].astype("Int64")

    # 4. Filter Administrative & Non-Commercial Adjustments
    print_step(4, "Filtering operational inventory adjustments (UnitPrice <= 0)")
    # Non-commercial records: write-offs (neg qty + price 0), bad debt adjustments (price < 0), giveaways (price == 0)
    admin_mask = df_dedup["unit_price"] <= 0
    admin_excl_count = admin_mask.sum()
    df_commercial = df_dedup[~admin_mask].copy()

    print(f"    Administrative records excluded: {admin_excl_count:,}")
    print(f"    Clean commercial transactions: {len(df_commercial):,}")

    # 5. Classify Transactions (Sales vs Returns) & Feature Engineering
    print_step(5, "Classifying transactions and engineering date features")
    is_c_invoice = df_commercial["invoice_no"].str.startswith(("C", "c"))
    is_neg_qty = df_commercial["quantity"] < 0

    df_commercial["is_return"] = is_c_invoice & is_neg_qty
    df_commercial["transaction_type"] = np.where(df_commercial["is_return"], "Return", "Sale")

    # Financial line total (returns naturally carry negative total)
    df_commercial["line_total"] = (df_commercial["quantity"] * df_commercial["unit_price"]).round(2)

    # Date / Calendar Dimension fields
    df_commercial["order_date"] = df_commercial["invoice_date"].dt.date
    df_commercial["date_key"] = df_commercial["invoice_date"].dt.strftime("%Y%m%d").astype(int)
    df_commercial["year"] = df_commercial["invoice_date"].dt.year
    df_commercial["quarter"] = df_commercial["invoice_date"].dt.quarter
    df_commercial["year_quarter"] = df_commercial["year"].astype(str) + "-Q" + df_commercial["quarter"].astype(str)
    df_commercial["month"] = df_commercial["invoice_date"].dt.month
    df_commercial["month_name"] = df_commercial["invoice_date"].dt.strftime("%B")
    df_commercial["year_month"] = df_commercial["invoice_date"].dt.strftime("%Y-%m")
    df_commercial["day_of_week"] = df_commercial["invoice_date"].dt.dayofweek + 1  # 1=Monday, 7=Sunday
    df_commercial["day_name"] = df_commercial["invoice_date"].dt.strftime("%A")
    df_commercial["hour"] = df_commercial["invoice_date"].dt.hour

    # Split into Sales and Returns subsets
    df_sales = df_commercial[df_commercial["transaction_type"] == "Sale"].copy()
    df_returns = df_commercial[df_commercial["transaction_type"] == "Return"].copy()

    sales_rev = df_sales["line_total"].sum()
    return_rev = df_returns["line_total"].sum()
    net_rev = df_commercial["line_total"].sum()

    print(f"    -> Sales transactions: {len(df_sales):,} rows | Gross Value: £{sales_rev:,.2f}")
    print(f"    -> Return transactions: {len(df_returns):,} rows | Return Value: £{return_rev:,.2f}")
    print(f"    -> Total Commercial: {len(df_commercial):,} rows | Net Value: £{net_rev:,.2f}")
    print(f"    -> Reconciliation Check: {sales_rev:.2f} + ({return_rev:.2f}) == {net_rev:.2f} -> {abs((sales_rev + return_rev) - net_rev) < 0.01}")

    # 6. Generate Star Schema & Export Processed CSVs
    print_step(6, "Generating Star Schema dimension & fact tables and exporting CSVs")

    # A. cleaned_transactions.csv (all valid commercial rows)
    cleaned_path = PROCESSED_DIR / "cleaned_transactions.csv"
    df_commercial.to_csv(cleaned_path, index=False)
    print(f"    [Saved] {cleaned_path.name} ({len(df_commercial):,} rows)")

    # B. sales_transactions.csv (sales only)
    sales_path = PROCESSED_DIR / "sales_transactions.csv"
    df_sales.to_csv(sales_path, index=False)
    print(f"    [Saved] {sales_path.name} ({len(df_sales):,} rows)")

    # C. returns_cancellations.csv (returns only)
    returns_path = PROCESSED_DIR / "returns_cancellations.csv"
    df_returns.to_csv(returns_path, index=False)
    print(f"    [Saved] {returns_path.name} ({len(df_returns):,} rows)")

    # D. DimDate
    unique_dates = df_commercial[["date_key", "order_date", "year", "quarter", "year_quarter", "month", "month_name", "year_month", "day_of_week", "day_name"]].drop_duplicates().sort_values("date_key")
    dim_date_path = PROCESSED_DIR / "dim_date.csv"
    unique_dates.to_csv(dim_date_path, index=False)
    print(f"    [Saved] {dim_date_path.name} ({len(unique_dates):,} unique dates)")

    # E. DimCustomer
    # Aggregate customer summary for registered accounts + 1 row for Guest Checkout
    registered_cust = df_commercial[df_commercial["customer_id"].notnull()].groupby("customer_id").agg(
        country=("country", "first"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
        total_orders=("invoice_no", "nunique"),
        total_items_bought=("quantity", "sum"),
        total_spend=("line_total", "sum")
    ).reset_index()
    registered_cust["customer_type"] = "Registered"

    # Add guest representation (ID = -1)
    guest_row = pd.DataFrame([{
        "customer_id": -1,
        "country": "Multiple",
        "first_order_date": df_commercial["order_date"].min(),
        "last_order_date": df_commercial["order_date"].max(),
        "total_orders": df_commercial[df_commercial["is_guest"]]["invoice_no"].nunique(),
        "total_items_bought": df_commercial[df_commercial["is_guest"]]["quantity"].sum(),
        "total_spend": df_commercial[df_commercial["is_guest"]]["line_total"].sum(),
        "customer_type": "Guest Checkout"
    }])
    dim_customer = pd.concat([registered_cust, guest_row], ignore_index=True)
    dim_customer_path = PROCESSED_DIR / "dim_customer.csv"
    dim_customer.to_csv(dim_customer_path, index=False)
    print(f"    [Saved] {dim_customer_path.name} ({len(dim_customer):,} customer records: {len(registered_cust):,} registered + 1 guest)")

    # F. DimProduct
    dim_product = df_commercial.groupby("stock_code").agg(
        description=("description", "first"),
        avg_unit_price=("unit_price", "mean"),
        min_unit_price=("unit_price", "min"),
        max_unit_price=("unit_price", "max"),
        total_units_sold=("quantity", "sum"),
        total_revenue=("line_total", "sum")
    ).reset_index()
    dim_product["avg_unit_price"] = dim_product["avg_unit_price"].round(2)
    dim_product["total_revenue"] = dim_product["total_revenue"].round(2)
    dim_product_path = PROCESSED_DIR / "dim_product.csv"
    dim_product.to_csv(dim_product_path, index=False)
    print(f"    [Saved] {dim_product_path.name} ({len(dim_product):,} distinct products)")

    # G. DimGeography
    unique_countries = sorted(df_commercial["country"].unique())
    dim_geography = pd.DataFrame({
        "country_key": range(1, len(unique_countries) + 1),
        "country": unique_countries,
        "market_region": [
            "Domestic UK" if c == "United Kingdom" else "European Union" if c in [
                "France", "Germany", "Spain", "EIRE", "Netherlands", "Belgium", "Switzerland",
                "Portugal", "Italy", "Poland", "Norway", "Sweden", "Finland", "Austria",
                "Denmark", "Cyprus", "Malta", "Greece", "Lithuania", "Czech Republic", "European Community"
            ] else "International Export"
            for c in unique_countries
        ]
    })
    dim_geo_path = PROCESSED_DIR / "dim_geography.csv"
    dim_geography.to_csv(dim_geo_path, index=False)
    print(f"    [Saved] {dim_geo_path.name} ({len(dim_geography)} countries)")

    # H. FactSales (Optimized Fact Table)
    geo_map = dict(zip(dim_geography["country"], dim_geography["country_key"]))
    fact_sales = df_commercial.copy()
    fact_sales["country_key"] = fact_sales["country"].map(geo_map)
    # Assign -1 to guest customer_id in fact table for referential integrity
    fact_sales["customer_id"] = fact_sales["customer_id"].fillna(-1).astype(int)

    fact_cols = [
        "invoice_no", "invoice_date", "date_key", "customer_id", "stock_code",
        "country_key", "quantity", "unit_price", "line_total", "is_return", "transaction_type"
    ]
    fact_sales = fact_sales[fact_cols]
    fact_path = PROCESSED_DIR / "fact_sales.csv"
    fact_sales.to_csv(fact_path, index=False)
    print(f"    [Saved] {fact_path.name} ({len(fact_sales):,} fact records)")

    # I. data_quality_report.csv
    quality_metrics = pd.DataFrame([
        {"Metric": "Raw Records Loaded", "Count": raw_count, "Financial_Value_GBP": None, "Notes": "Original UCI Online Retail file"},
        {"Metric": "Exact Duplicate Records Removed", "Count": exact_dups, "Financial_Value_GBP": None, "Notes": "Identical order lines from web double-clicks"},
        {"Metric": "Records After Deduplication", "Count": len(df_dedup), "Financial_Value_GBP": None, "Notes": "Deduplicated working set"},
        {"Metric": "Administrative Records Excluded (UnitPrice <= 0)", "Count": admin_excl_count, "Financial_Value_GBP": None, "Notes": "Inventory write-offs, lost items, bad debt"},
        {"Metric": "Cleaned Commercial Transactions", "Count": len(df_commercial), "Financial_Value_GBP": round(net_rev, 2), "Notes": "Valid sales + returns"},
        {"Metric": "-> Positive Sales Transactions", "Count": len(df_sales), "Financial_Value_GBP": round(sales_rev, 2), "Notes": "Gross revenue generation"},
        {"Metric": "-> Customer Returns & Cancellations", "Count": len(df_returns), "Financial_Value_GBP": round(return_rev, 2), "Notes": "Negative value refund stream"},
        {"Metric": "Net Commercial Revenue Reconciled", "Count": len(df_commercial), "Financial_Value_GBP": round(net_rev, 2), "Notes": "Gross Sales + Return Value"}
    ])
    quality_csv_path = PROCESSED_DIR / "data_quality_report.csv"
    quality_metrics.to_csv(quality_csv_path, index=False)
    print(f"    [Saved] {quality_csv_path.name}")

    print("\n" + "=" * 68)
    print(" Pipeline Execution Complete! All processed CSVs generated successfully. ")
    print("=" * 68)
    return True


if __name__ == "__main__":
    clean_retail_data()
