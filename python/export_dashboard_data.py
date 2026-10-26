"""
RetailPulse - Export SQL Report Data to Web Dashboard JSON
Reads the 15 query CSV reports in reports/sql/ and outputs a consolidated JSON file
for the interactive web dashboard.
"""

import json
from pathlib import Path
import pandas as pd
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_REPORTS_DIR = PROJECT_ROOT / "reports" / "sql"
WEB_DIR = PROJECT_ROOT / "web"
WEB_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON = WEB_DIR / "dashboard_data.json"


def export_dashboard_data():
    print("[1/2] Reading SQL reports from reports/sql/...")

    data = {}

    # Query 01: Overall KPIs
    df_q1 = pd.read_csv(SQL_REPORTS_DIR / "query_01_total_sales_revenue_returns_net_revenue_.csv")
    data["kpis"] = df_q1.to_dict(orient="records")[0]

    # Query 02: Monthly Trends
    df_q2 = pd.read_csv(SQL_REPORTS_DIR / "query_02_monthly_net_revenue_trends_order_volume.csv")
    data["monthly_trends"] = df_q2.to_dict(orient="records")

    # Query 03: Quarterly & Yearly Performance
    df_q3 = pd.read_csv(SQL_REPORTS_DIR / "query_03_quarterly_and_yearly_financial_performan.csv")
    data["quarterly_trends"] = df_q3.to_dict(orient="records")

    # Query 04: Top Products by Unit Volume
    df_q4 = pd.read_csv(SQL_REPORTS_DIR / "query_04_top_10_best_selling_products_by_unit_vol.csv")
    data["top_products_units"] = df_q4.to_dict(orient="records")

    # Query 05: Top Products by Net Revenue
    df_q5 = pd.read_csv(SQL_REPORTS_DIR / "query_05_top_10_products_by_net_revenue_contribut.csv")
    data["top_products_revenue"] = df_q5.to_dict(orient="records")

    # Query 06: Country Level Revenue
    df_q6 = pd.read_csv(SQL_REPORTS_DIR / "query_06_country_level_revenue_market_region_segm.csv")
    data["country_revenue"] = df_q6.to_dict(orient="records")

    # Query 07: AOV by Geographic Region
    df_q7 = pd.read_csv(SQL_REPORTS_DIR / "query_07_average_order_value_aov_by_geographic_ma.csv")
    data["aov_by_region"] = df_q7.to_dict(orient="records")

    # Query 08: Customer Account Distribution
    df_q8 = pd.read_csv(SQL_REPORTS_DIR / "query_08_unique_customer_count_registered_loyalty.csv")
    data["customer_account_dist"] = df_q8.to_dict(orient="records")

    # Query 09: Guest Checkout Impact
    df_q9 = pd.read_csv(SQL_REPORTS_DIR / "query_09_impact_of_missing_customer_ids_guest_che.csv")
    data["guest_checkout_impact"] = df_q9.to_dict(orient="records")

    # Query 10: Repeat Customer Distribution
    df_q10 = pd.read_csv(SQL_REPORTS_DIR / "query_10_customer_purchase_frequency_repeat_custo.csv")
    data["repeat_customer_dist"] = df_q10.to_dict(orient="records")

    # Query 11: New vs Returning Cohorts
    df_q11 = pd.read_csv(SQL_REPORTS_DIR / "query_11_new_vs_returning_customer_monthly_acquis.csv")
    data["monthly_cohorts"] = df_q11.to_dict(orient="records")

    # Query 12: Top 10 VIP Customers
    df_q12 = pd.read_csv(SQL_REPORTS_DIR / "query_12_top_10_registered_customers_by_lifetime_.csv")
    data["top_customers"] = df_q12.to_dict(orient="records")

    # Query 13: Customer Decile Segmentation
    df_q13 = pd.read_csv(SQL_REPORTS_DIR / "query_13_customer_revenue_ranking_and_decile_segm.csv")
    data["customer_deciles"] = df_q13.to_dict(orient="records")

    # Query 14: Cumulative Monthly Revenue
    df_q14 = pd.read_csv(SQL_REPORTS_DIR / "query_14_running_cumulative_monthly_revenue_runni.csv")
    data["cumulative_revenue"] = df_q14.to_dict(orient="records")

    # Query 15: Returns by Country
    df_q15 = pd.read_csv(SQL_REPORTS_DIR / "query_15_returns_and_cancellation_rate_analysis_b.csv")
    data["returns_by_country"] = df_q15.to_dict(orient="records")

    # Extract all 15 queries metadata & results for interactive SQL Studio
    print("[2/3] Parsing SQL query metadata from sql/analysis_queries.sql...")
    sql_file = PROJECT_ROOT / "sql" / "analysis_queries.sql"
    sql_text = sql_file.read_text(encoding="utf-8")

    query_blocks = re.split(r"-- QUERY (\d+):", sql_text)
    # query_blocks[0] is preamble, then alternating (num, body)
    sql_library = []
    
    csv_map = {
        1: "query_01_total_sales_revenue_returns_net_revenue_.csv",
        2: "query_02_monthly_net_revenue_trends_order_volume.csv",
        3: "query_03_quarterly_and_yearly_financial_performan.csv",
        4: "query_04_top_10_best_selling_products_by_unit_vol.csv",
        5: "query_05_top_10_products_by_net_revenue_contribut.csv",
        6: "query_06_country_level_revenue_market_region_segm.csv",
        7: "query_07_average_order_value_aov_by_geographic_ma.csv",
        8: "query_08_unique_customer_count_registered_loyalty.csv",
        9: "query_09_impact_of_missing_customer_ids_guest_che.csv",
        10: "query_10_customer_purchase_frequency_repeat_custo.csv",
        11: "query_11_new_vs_returning_customer_monthly_acquis.csv",
        12: "query_12_top_10_registered_customers_by_lifetime_.csv",
        13: "query_13_customer_revenue_ranking_and_decile_segm.csv",
        14: "query_14_running_cumulative_monthly_revenue_runni.csv",
        15: "query_15_returns_and_cancellation_rate_analysis_b.csv",
    }

    for i in range(1, len(query_blocks), 2):
        q_num = int(query_blocks[i])
        block = query_blocks[i + 1]

        lines = block.splitlines()
        title = lines[0].strip() if lines else f"Query {q_num}"
        
        business_question = ""
        concepts = ""
        sql_lines = []
        in_sql = False

        for line in lines[1:]:
            s = line.strip()
            if s.startswith("-- Business Question:"):
                business_question = s.replace("-- Business Question:", "").strip()
            elif s.startswith("-- Concepts Demonstrated:"):
                concepts = s.replace("-- Concepts Demonstrated:", "").strip()
            elif s.startswith("--") and not in_sql:
                continue
            else:
                in_sql = True
                sql_lines.append(line)

        raw_sql = "\n".join(sql_lines).strip()
        if raw_sql.endswith(";"):
            raw_sql = raw_sql[:-1].strip()

        # Load CSV results
        csv_file = SQL_REPORTS_DIR / csv_map.get(q_num, "")
        records = []
        columns = []
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            columns = list(df.columns)
            records = df.to_dict(orient="records")

        sql_library.append({
            "num": q_num,
            "title": title,
            "business_question": business_question,
            "concepts": concepts,
            "sql": raw_sql,
            "columns": columns,
            "rows": records
        })

    data["sql_queries_library"] = sql_library

    print("[3/3] Writing consolidated JSON to web/dashboard_data.json...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Exported dashboard data successfully ({OUTPUT_JSON.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    import re
    export_dashboard_data()
