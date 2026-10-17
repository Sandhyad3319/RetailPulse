"""
RetailPulse: SQLite Database & Analytical Query Test Suite (pytest)
==================================================================
Validates that 'data/processed/retailpulse.db' satisfies schema constraints,
primary/foreign key integrity, financial reconciliation, and query execution.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = PROCESSED_DIR / "retailpulse.db"
QUERIES_PATH = SQL_DIR / "analysis_queries.sql"


@pytest.fixture(scope="session")
def db_connection():
    """Provides a read-only SQLite connection for testing."""
    assert DB_PATH.exists(), f"Database does not exist at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()


def test_database_tables_exist(db_connection):
    """Verify all 5 required Star Schema tables exist in SQLite."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = ["dim_date", "dim_geography", "dim_product", "dim_customer", "fact_sales"]
    for t in expected_tables:
        assert t in tables, f"Expected table '{t}' is missing from database."


def test_database_row_counts_match_csvs(db_connection):
    """Verify database row counts match the processed CSV files exactly."""
    cursor = db_connection.cursor()
    tables = ["dim_date", "dim_geography", "dim_product", "dim_customer", "fact_sales"]
    for tbl in tables:
        db_count = cursor.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        csv_count = len(pd.read_csv(PROCESSED_DIR / f"{tbl}.csv"))
        assert db_count == csv_count, f"Row count mismatch in table {tbl}: DB={db_count}, CSV={csv_count}"


def test_financial_reconciliation_in_sql(db_connection):
    """Verify that Gross Sales + Returns == Net Revenue inside SQLite."""
    cursor = db_connection.cursor()
    query = """
    SELECT 
        ROUND(SUM(CASE WHEN is_return = 0 THEN line_total ELSE 0 END), 2) AS gross_sales,
        ROUND(SUM(CASE WHEN is_return = 1 THEN line_total ELSE 0 END), 2) AS returns_total,
        ROUND(SUM(line_total), 2) AS net_total
    FROM fact_sales;
    """
    gross, returns, net = cursor.execute(query).fetchone()
    assert gross == 10642110.80, f"Expected Gross Sales £10,642,110.80, got {gross}"
    assert returns == -893979.73, f"Expected Returns -£893,979.73, got {returns}"
    assert net == 9748131.07, f"Expected Net Total £9,748,131.07, got {net}"
    assert pytest.approx(gross + returns, rel=1e-5) == net


def test_foreign_key_integrity(db_connection):
    """Verify foreign keys from fact_sales to dimensions have 0 orphan records."""
    cursor = db_connection.cursor()

    # Customer FK
    orphan_cust = cursor.execute("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_customer c ON f.customer_id = c.customer_id 
        WHERE c.customer_id IS NULL;
    """).fetchone()[0]
    assert orphan_cust == 0, f"Found {orphan_cust} orphan customer foreign keys."

    # Product FK
    orphan_prod = cursor.execute("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_product p ON f.stock_code = p.stock_code 
        WHERE p.stock_code IS NULL;
    """).fetchone()[0]
    assert orphan_prod == 0, f"Found {orphan_prod} orphan product foreign keys."

    # Date FK
    orphan_date = cursor.execute("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_date d ON f.date_key = d.date_key 
        WHERE d.date_key IS NULL;
    """).fetchone()[0]
    assert orphan_date == 0, f"Found {orphan_date} orphan date foreign keys."

    # Geography FK
    orphan_geo = cursor.execute("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_geography g ON f.country_key = g.country_key 
        WHERE g.country_key IS NULL;
    """).fetchone()[0]
    assert orphan_geo == 0, f"Found {orphan_geo} orphan geography foreign keys."


def test_primary_key_uniqueness(db_connection):
    """Verify primary keys in dimension tables are 100% unique (no duplicates)."""
    cursor = db_connection.cursor()
    pk_checks = [
        ("dim_customer", "customer_id"),
        ("dim_product", "stock_code"),
        ("dim_date", "date_key"),
        ("dim_geography", "country_key")
    ]
    for tbl, pk in pk_checks:
        dup_count = cursor.execute(f"""
            SELECT COUNT(*) - COUNT(DISTINCT {pk}) FROM {tbl};
        """).fetchone()[0]
        assert dup_count == 0, f"Primary key {pk} in table {tbl} contains duplicate values."


def test_guest_checkout_representation(db_connection):
    """Verify guest checkout transactions map cleanly to customer_id = -1."""
    cursor = db_connection.cursor()
    guest_dim = cursor.execute("SELECT customer_type FROM dim_customer WHERE customer_id = -1").fetchone()
    assert guest_dim is not None, "Sentinel customer record (customer_id = -1) missing in dim_customer."
    assert guest_dim[0] == "Guest Checkout"

    guest_fact_count = cursor.execute("SELECT COUNT(*) FROM fact_sales WHERE customer_id = -1").fetchone()[0]
    assert guest_fact_count == 132565, f"Expected 132,565 guest fact lines, got {guest_fact_count}"


def test_all_15_queries_execute(db_connection):
    """Verify all 15 queries in analysis_queries.sql execute without syntax or runtime error."""
    import re
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    pattern = r"-- QUERY (\d+): ([^\n]+)\n(.*?)(?=(?:-- QUERY \d+:|\Z))"
    matches = re.findall(pattern, text, re.DOTALL)
    assert len(matches) == 15, f"Expected 15 queries in analysis_queries.sql, found {len(matches)}"

    cursor = db_connection.cursor()
    for q_num, q_title, q_body in matches:
        sql_lines = [l for l in q_body.splitlines() if not l.strip().startswith("--")]
        clean_sql = "\n".join(sql_lines).strip()
        if clean_sql.endswith(";"):
            clean_sql = clean_sql[:-1]
        try:
            cursor.execute(clean_sql)
            rows = cursor.fetchall()
            assert len(rows) > 0, f"Query {q_num} ('{q_title}') returned 0 rows."
        except Exception as e:
            pytest.fail(f"Query {q_num} ('{q_title}') failed with error: {e}")
