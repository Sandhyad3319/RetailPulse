"""
RetailPulse: SQLite Database Loader
===================================
Loads cleaned dimensional and fact CSV datasets into the relational SQLite database
'data/processed/retailpulse.db' using the Star Schema defined in 'sql/schema.sql'.

Ensures:
- Full schema creation with primary and foreign key constraints.
- Optimized indexes for analytical querying.
- Accurate row count and financial reconciliation between CSV files and database tables.
- Idempotent execution (can be run repeatedly without duplicating records).
"""

import sys
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = PROCESSED_DIR / "retailpulse.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"


def load_database():
    print("=" * 68)
    print(" RetailPulse: Loading Cleaned Data into SQLite Relational Database ")
    print("=" * 68)

    if not SCHEMA_PATH.exists():
        print(f"[-] ERROR: Schema DDL file not found at: {SCHEMA_PATH}")
        sys.exit(1)

    print(f"\n[1/4] Initializing SQLite database at: {DB_PATH.name}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema DDL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    print("    Star Schema tables created successfully.")

    # 2. Load Dimensions
    print("\n[2/4] Populating Dimension tables...")

    # DimDate
    df_date = pd.read_csv(PROCESSED_DIR / "dim_date.csv")
    df_date.to_sql("dim_date", conn, if_exists="append", index=False)
    print(f"    [Loaded] dim_date:      {len(df_date):,} rows")

    # DimGeography
    df_geo = pd.read_csv(PROCESSED_DIR / "dim_geography.csv")
    df_geo.to_sql("dim_geography", conn, if_exists="append", index=False)
    print(f"    [Loaded] dim_geography: {len(df_geo):,} rows")

    # DimProduct
    df_prod = pd.read_csv(PROCESSED_DIR / "dim_product.csv")
    df_prod.to_sql("dim_product", conn, if_exists="append", index=False)
    print(f"    [Loaded] dim_product:   {len(df_prod):,} rows")

    # DimCustomer
    df_cust = pd.read_csv(PROCESSED_DIR / "dim_customer.csv")
    df_cust.to_sql("dim_customer", conn, if_exists="append", index=False)
    print(f"    [Loaded] dim_customer:  {len(df_cust):,} rows")

    # 3. Load Fact Table
    print("\n[3/4] Populating FactSales table (530k+ rows)...")
    df_fact = pd.read_csv(PROCESSED_DIR / "fact_sales.csv")
    # Cast is_return to int for SQLite storage
    df_fact["is_return"] = df_fact["is_return"].astype(int)

    # Use chunksize for optimal memory and speed
    df_fact.to_sql("fact_sales", conn, if_exists="append", index=False, chunksize=50000)
    print(f"    [Loaded] fact_sales:    {len(df_fact):,} rows")

    # 4. Reconciliation Verification
    print("\n[4/4] Auditing Database Table Reconciliation...")
    tables = ["dim_date", "dim_geography", "dim_product", "dim_customer", "fact_sales"]
    reconciled = True

    for tbl in tables:
        db_count = cursor.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        csv_file = f"{tbl}.csv"
        csv_count = len(pd.read_csv(PROCESSED_DIR / csv_file))
        status = "PASS" if db_count == csv_count else "FAIL"
        if status == "FAIL":
            reconciled = False
        print(f"    {tbl:<16}: DB={db_count:,} | CSV={csv_count:,} [{status}]")

    # Check Financial Total
    db_revenue = cursor.execute("SELECT ROUND(SUM(line_total), 2) FROM fact_sales").fetchone()[0]
    csv_revenue = round(df_fact["line_total"].sum(), 2)
    fin_status = "PASS" if abs(db_revenue - csv_revenue) < 0.05 else "FAIL"
    print(f"\n    Financial Total : DB=£{db_revenue:,.2f} | CSV=£{csv_revenue:,.2f} [{fin_status}]")

    conn.close()

    print("\n" + "=" * 68)
    if reconciled and fin_status == "PASS":
        print(" [+] SQLite Database Loaded & Validated with 100% Reconciliation! ")
        print(f"     Database file: {DB_PATH} ({DB_PATH.stat().st_size / (1024*1024):.2f} MB)")
    else:
        print(" [-] Database loading completed with discrepancies. Please check logs.")
    print("=" * 68)
    return reconciled and (fin_status == "PASS")


if __name__ == "__main__":
    success = load_database()
    if not success:
        sys.exit(1)
