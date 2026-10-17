"""
RetailPulse: Automated Data Quality Test Suite (pytest)
======================================================
Runs automated unit and integration tests on processed data files,
validating schema adherence, financial reconciliation, and star schema integrity.
"""

import pytest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


@pytest.fixture(scope="session")
def processed_datasets():
    """Loads all processed datasets once for the test session."""
    datasets = {
        "cleaned": pd.read_csv(PROCESSED_DIR / "cleaned_transactions.csv", low_memory=False),
        "sales": pd.read_csv(PROCESSED_DIR / "sales_transactions.csv", low_memory=False),
        "returns": pd.read_csv(PROCESSED_DIR / "returns_cancellations.csv", low_memory=False),
        "fact": pd.read_csv(PROCESSED_DIR / "fact_sales.csv", low_memory=False),
        "customer": pd.read_csv(PROCESSED_DIR / "dim_customer.csv", low_memory=False),
        "product": pd.read_csv(PROCESSED_DIR / "dim_product.csv", low_memory=False),
        "date": pd.read_csv(PROCESSED_DIR / "dim_date.csv", low_memory=False),
        "geography": pd.read_csv(PROCESSED_DIR / "dim_geography.csv", low_memory=False),
    }
    return datasets


def test_processed_files_exist():
    """Verify all 8 processed CSV files exist and have non-zero size."""
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
    for filename in expected_files:
        filepath = PROCESSED_DIR / filename
        assert filepath.exists(), f"Expected file {filename} is missing."
        assert filepath.stat().st_size > 0, f"Expected file {filename} is empty."


def test_row_count_integrity(processed_datasets):
    """Verify that sales + returns exactly equals cleaned transactions and fact table rows."""
    cleaned = processed_datasets["cleaned"]
    sales = processed_datasets["sales"]
    returns = processed_datasets["returns"]
    fact = processed_datasets["fact"]

    assert len(sales) + len(returns) == len(cleaned), "Sales count + Return count must equal Cleaned count."
    assert len(fact) == len(cleaned), "Fact table row count must equal Cleaned count."


def test_financial_reconciliation(processed_datasets):
    """Verify financial reconciliation: Gross Sales + Returns Value == Net Revenue."""
    sales = processed_datasets["sales"]
    returns = processed_datasets["returns"]
    cleaned = processed_datasets["cleaned"]
    fact = processed_datasets["fact"]

    gross_sales = sales["line_total"].sum()
    returns_val = returns["line_total"].sum()
    net_sales = cleaned["line_total"].sum()
    fact_sales_val = fact["line_total"].sum()

    assert gross_sales > 0, "Gross sales must be positive."
    assert returns_val < 0, "Returns total must be negative."
    assert pytest.approx(gross_sales + returns_val, rel=1e-5) == net_sales, "Gross + Returns must reconcile to Net sales."
    assert pytest.approx(net_sales, rel=1e-5) == fact_sales_val, "Net sales must reconcile to Fact table sales."


def test_cancellation_and_return_classification(processed_datasets):
    """Verify that 100% of returns have negative quantity and 'C' invoice prefix."""
    returns = processed_datasets["returns"]
    assert (returns["quantity"] < 0).all(), "All return rows must have negative quantity."
    assert returns["invoice_no"].astype(str).str.startswith(("C", "c")).all(), "All return rows must start with 'C'."
    assert (returns["is_return"] == True).all(), "All return rows must have is_return = True."


def test_sales_classification(processed_datasets):
    """Verify that 100% of sales rows have positive quantity and unit price."""
    sales = processed_datasets["sales"]
    assert (sales["quantity"] > 0).all(), "All sales rows must have positive quantity."
    assert (sales["unit_price"] > 0).all(), "All sales rows must have positive unit price."
    assert (sales["is_return"] == False).all(), "All sales rows must have is_return = False."


def test_no_exact_duplicates_in_cleaned(processed_datasets):
    """Verify that cleaned dataset contains zero exact duplicate rows."""
    cleaned = processed_datasets["cleaned"]
    assert cleaned.duplicated().sum() == 0, "Cleaned dataset must have 0 exact duplicate rows."


def test_star_schema_referential_integrity(processed_datasets):
    """Verify that all foreign keys in Fact table resolve to corresponding Dimension tables."""
    fact = processed_datasets["fact"]
    customer = processed_datasets["customer"]
    product = processed_datasets["product"]
    date_dim = processed_datasets["date"]
    geography = processed_datasets["geography"]

    # Customer key
    fact_cust_keys = set(fact["customer_id"])
    dim_cust_keys = set(customer["customer_id"])
    assert fact_cust_keys.issubset(dim_cust_keys), "Every customer_id in FactSales must exist in DimCustomer."

    # Product key
    fact_prod_keys = set(fact["stock_code"])
    dim_prod_keys = set(product["stock_code"])
    assert fact_prod_keys.issubset(dim_prod_keys), "Every stock_code in FactSales must exist in DimProduct."

    # Date key
    fact_date_keys = set(fact["date_key"])
    dim_date_keys = set(date_dim["date_key"])
    assert fact_date_keys.issubset(dim_date_keys), "Every date_key in FactSales must exist in DimDate."

    # Geography key
    fact_geo_keys = set(fact["country_key"])
    dim_geo_keys = set(geography["country_key"])
    assert fact_geo_keys.issubset(dim_geo_keys), "Every country_key in FactSales must exist in DimGeography."


def test_date_range_bounds(processed_datasets):
    """Verify that dates fall strictly within the genuine dataset timeframe (2010 to 2011)."""
    cleaned = processed_datasets["cleaned"]
    invoice_dates = pd.to_datetime(cleaned["invoice_date"])
    assert invoice_dates.min() >= pd.Timestamp("2010-12-01"), "Earliest date cannot precede Dec 1, 2010."
    assert invoice_dates.max() <= pd.Timestamp("2011-12-31"), "Latest date cannot exceed Dec 31, 2011."
