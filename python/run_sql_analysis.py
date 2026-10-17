"""
RetailPulse: SQL Analytical Query Runner
========================================
Connects to 'data/processed/retailpulse.db', executes all 15 analytical SQL queries
from 'sql/analysis_queries.sql', prints formatted result previews to the console,
and exports all query outputs as CSV files to 'reports/sql/'.
"""

import re
import sys
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"
REPORTS_SQL_DIR = BASE_DIR / "reports" / "sql"
DB_PATH = PROCESSED_DIR / "retailpulse.db"
QUERIES_PATH = SQL_DIR / "analysis_queries.sql"


def parse_sql_file(file_path: Path):
    """Parses individual queries from the SQL file using header comments."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split by QUERY headers
    pattern = r"-- QUERY (\d+): ([^\n]+)\n(.*?)(?=(?:-- QUERY \d+:|\Z))"
    matches = re.findall(pattern, text, re.DOTALL)

    parsed_queries = []
    for q_num, q_title, q_body in matches:
        # Extract pure SQL (strip comments preceding SELECT / WITH)
        sql_lines = []
        for line in q_body.splitlines():
            stripped = line.strip()
            if stripped.startswith("--") and not sql_lines:
                continue
            sql_lines.append(line)
        sql_clean = "\n".join(sql_lines).strip()
        if sql_clean.endswith(";"):
            sql_clean = sql_clean[:-1].strip()

        parsed_queries.append({
            "num": int(q_num),
            "title": q_title.strip(),
            "sql": sql_clean
        })

    return parsed_queries


def run_sql_analysis():
    print("=" * 68)
    print(" RetailPulse: Executing Analytical Business Queries in SQLite ")
    print("=" * 68)

    if not DB_PATH.exists():
        print(f"[-] ERROR: SQLite database not found at: {DB_PATH}")
        print("    Please run 'python python/load_sqlite.py' first.")
        sys.exit(1)

    if not QUERIES_PATH.exists():
        print(f"[-] ERROR: SQL file not found at: {QUERIES_PATH}")
        sys.exit(1)

    REPORTS_SQL_DIR.mkdir(parents=True, exist_ok=True)
    queries = parse_sql_file(QUERIES_PATH)
    print(f"\n[+] Successfully parsed {len(queries)} analytical queries from '{QUERIES_PATH.name}'.")

    conn = sqlite3.connect(DB_PATH)
    success_count = 0
    failed_count = 0
    results_summary = []

    for q in queries:
        q_num = q["num"]
        q_title = q["title"]
        q_sql = q["sql"]

        # Filename slug
        slug = re.sub(r"[^a-zA-Z0-9_]+", "_", q_title.lower()).strip("_")
        out_csv_name = f"query_{q_num:02d}_{slug[:40]}.csv"
        out_csv_path = REPORTS_SQL_DIR / out_csv_name

        print(f"\n---> Executing Query {q_num:02d}: {q_title}")
        try:
            df_result = pd.read_sql_query(q_sql, conn)
            row_count = len(df_result)
            df_result.to_csv(out_csv_path, index=False)
            success_count += 1
            print(f"     [SUCCESS] Returned {row_count} rows | Saved to '{out_csv_name}'")

            # Display preview
            if row_count > 0:
                print("     Sample Output:")
                preview = df_result.head(3).to_string(index=False)
                for line in preview.splitlines():
                    print(f"       {line}")
            results_summary.append({
                "Query": q_num,
                "Title": q_title,
                "Status": "PASS",
                "Rows": row_count,
                "ExportedFile": out_csv_name
            })
        except Exception as e:
            failed_count += 1
            print(f"     [FAILED] Error: {e}")
            results_summary.append({
                "Query": q_num,
                "Title": q_title,
                "Status": f"FAIL: {e}",
                "Rows": 0,
                "ExportedFile": "N/A"
            })

    conn.close()

    # Save summary table
    summary_df = pd.DataFrame(results_summary)
    summary_csv = REPORTS_SQL_DIR / "sql_execution_summary.csv"
    summary_df.to_csv(summary_csv, index=False)

    print("\n" + "=" * 68)
    print(f" Execution Complete: {success_count} Succeeded, {failed_count} Failed out of {len(queries)} Queries.")
    print(f" All CSV exports and summary saved in: {REPORTS_SQL_DIR}")
    print("=" * 68)

    return failed_count == 0


if __name__ == "__main__":
    all_ok = run_sql_analysis()
    if not all_ok:
        sys.exit(1)
