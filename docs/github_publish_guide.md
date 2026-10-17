# RetailPulse: GitHub Portfolio Publishing Guide

This guide walks you through publishing **RetailPulse** to GitHub as a portfolio project for Data Analyst, Business Intelligence Analyst, and SQL Developer job applications.

---

## 1. Safety & Credential Checklist (Before Publishing)

Before making any commit, verify these safety rules:
- [x] **No Private Passwords or API Keys**: The project uses local SQLite and public datasets; zero private credentials exist.
- [x] **Exclude Oversized Raw Files**: GitHub blocks files over 100 MB and warns on files over 50 MB. Our `.gitignore` automatically excludes `data/raw/*.xlsx` and `data/raw/*.zip` because users can download the raw data on demand with `python python/download_data.py`.
- [x] **Include Processed CSVs & Database**: The processed CSV files and SQLite database (`data/processed/retailpulse.db` at 83.6 MB) can be included so reviewers and recruiters can immediately evaluate your queries without needing to run the ingestion pipeline.

---

## 2. Step-by-Step Git & GitHub Setup (Windows)

### Step 1: Check or Install Git
Open PowerShell and check if Git is installed:
```powershell
git --version
```

- If Git returns `git version 2.x.x`, proceed to Step 2.
- If Git is not recognized:
  1. Download Git for Windows from: [https://git-scm.com/download/win](https://git-scm.com/download/win)
  2. Run the installer with default settings.
  3. Close and reopen PowerShell.

---

### Step 2: Configure Your Git Identity
If this is your first time using Git on this PC:
```powershell
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

---

### Step 3: Initialize the Local Git Repository
Navigate to your project root folder:
```powershell
cd c:\Users\USER\Documents\RetailPulse
git init -b main
```

---

### Step 4: Review Staged Files
Check the list of untracked files to verify `.gitignore` is working:
```powershell
git status
```
*Verify that `data/raw/Online Retail.xlsx` and `data/raw/online_retail.zip` do NOT appear in the untracked files list.*

---

### Step 5: Create Your Initial Commit
Stage all project code, SQL queries, documentation, and tests:
```powershell
git add .
git commit -m "feat: initial commit for RetailPulse end-to-end analytics platform"
```

---

### Step 6: Create a New GitHub Repository
1. Log in to [https://github.com/](https://github.com/).
2. In the top-right corner, click the **+** icon -> Select **New repository**.
3. Fill in the repository details:
   - **Repository name**: `RetailPulse-Sales-Customer-Intelligence`
   - **Description**: *"End-to-end retail sales and customer intelligence platform using Python, SQLite Star Schema, advanced SQL, and Power BI."*
   - **Visibility**: **Public** (required for portfolio review).
   - **Initialize repository with**: Leave all checkboxes (**README**, **.gitignore**, **license**) **UNCHECKED** (we already created them locally).
4. Click **Create repository**.

---

### Step 7: Connect and Push to GitHub
Copy the commands displayed on GitHub under **"push an existing repository from the command line"**:
```powershell
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/RetailPulse-Sales-Customer-Intelligence.git
git push -u origin main
```

---

## 3. Adding Power BI Screenshots After Building the `.pbix`

Once you have assembled your dashboard in Power BI Desktop:
1. Open each of the 4 report pages in Power BI Desktop.
2. Use the Windows Snipping Tool (`Win + Shift + S`) to capture a screenshot of each page.
3. Save the images inside your repository at:
   - `reports/figures/page1_executive_overview.png`
   - `reports/figures/page2_sales_performance.png`
   - `reports/figures/page3_customer_intelligence.png`
   - `reports/figures/page4_returns_insights.png`
4. Update the screenshot placeholders in `README.md` to point to these files:
   ```markdown
   ![Executive Overview](reports/figures/page1_executive_overview.png)
   ![Customer Intelligence](reports/figures/page3_customer_intelligence.png)
   ```
5. Commit and push the screenshots:
   ```powershell
   git add reports/figures/ README.md
   git commit -m "docs: add Power BI dashboard visual screenshots"
   git push
   ```
