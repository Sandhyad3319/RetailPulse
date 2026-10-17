"""
RetailPulse: Dataset Ingestion Script
====================================
Downloads the genuine UCI Online Retail dataset directly from the UCI Machine
Learning Repository, extracts the archive, and validates the raw Excel file.

Source: https://archive.ics.uci.edu/dataset/352/online+retail
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
Citation: Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online retail industry.
"""

import os
import sys
import zipfile
import urllib.request
import shutil
from pathlib import Path

DATASET_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
ZIP_PATH = RAW_DIR / "online_retail.zip"
EXCEL_PATH = RAW_DIR / "Online Retail.xlsx"


def print_step(msg: str):
    print(f"\n[+] {msg}")


def download_dataset():
    """Downloads and extracts the UCI Online Retail dataset."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if EXCEL_PATH.exists() and EXCEL_PATH.stat().st_size > 10_000_000:
        print_step(f"Raw dataset already present at: {EXCEL_PATH}")
        print(f"    File size: {EXCEL_PATH.stat().st_size / (1024 * 1024):.2f} MB")
        return True

    print_step(f"Connecting to UCI Repository: {DATASET_URL}")
    print("    Downloading online+retail.zip (approx. 22.6 MB)... Please wait.")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, (downloaded / total_size) * 100)
            mb_down = downloaded / (1024 * 1024)
            mb_tot = total_size / (1024 * 1024)
            sys.stdout.write(f"\r    Progress: {percent:5.1f}% ({mb_down:5.1f} MB / {mb_tot:5.1f} MB)")
            sys.stdout.flush()

    try:
        req = urllib.request.Request(
            DATASET_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RetailPulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as response, open(ZIP_PATH, "wb") as out_file:
            total_size = int(response.headers.get("Content-Length", 0))
            block_size = 65536
            downloaded = 0
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)
                if total_size > 0:
                    percent = min(100.0, (downloaded / total_size) * 100)
                    mb_down = downloaded / (1024 * 1024)
                    mb_tot = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r    Progress: {percent:5.1f}% ({mb_down:5.1f} MB / {mb_tot:5.1f} MB)")
                    sys.stdout.flush()
        print("\n    Download completed successfully!")
    except Exception as e:
        print(f"\n[-] ERROR: Failed to download dataset automatically: {e}")
        print("\n=== MANUAL DOWNLOAD INSTRUCTIONS ===")
        print("1. Open your web browser and navigate to:")
        print("   https://archive.ics.uci.edu/dataset/352/online+retail")
        print("2. Click the 'Download (22.6 MB)' button to get 'online+retail.zip'.")
        print(f"3. Unzip the file and place 'Online Retail.xlsx' inside:")
        print(f"   {RAW_DIR}")
        print("4. Re-run this script to verify the file.")
        return False

    # Extract ZIP
    print_step(f"Extracting '{ZIP_PATH.name}' to '{RAW_DIR}'...")
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(RAW_DIR)
            extracted_files = zip_ref.namelist()
            print(f"    Extracted files: {', '.join(extracted_files)}")

        # Verify Excel file exists
        if EXCEL_PATH.exists():
            size_mb = EXCEL_PATH.stat().st_size / (1024 * 1024)
            print_step(f"Dataset successfully verified: {EXCEL_PATH.name} ({size_mb:.2f} MB)")
            return True
        else:
            # Check if extracted file has different capitalization
            for f in RAW_DIR.glob("*.xlsx"):
                print(f"    Found Excel file: {f.name}")
                if f.name.lower() == "online retail.xlsx" and f != EXCEL_PATH:
                    shutil.move(str(f), str(EXCEL_PATH))
                    print(f"    Renamed to standardized name: {EXCEL_PATH.name}")
                    return True
            print("[-] WARNING: Could not find 'Online Retail.xlsx' in extracted contents.")
            return False
    except zipfile.BadZipFile:
        print("[-] ERROR: Downloaded file is corrupted or not a valid ZIP archive.")
        return False


if __name__ == "__main__":
    success = download_dataset()
    if not success:
        sys.exit(1)
