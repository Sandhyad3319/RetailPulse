# RetailPulse: Power BI Desktop Complete Build Guide

Welcome to the **Power BI Desktop** implementation guide for **RetailPulse: Sales & Customer Intelligence Analytics Platform**.

This guide is designed for complete beginners on Windows. By following these exact click-by-click instructions, you will construct a clean, four-page, executive-ready dashboard in Power BI Desktop and save it as `RetailPulse.pbix`.

---

## 1. Transparency Regarding `.pbix` Generation

> [!NOTE]
> **Why we build the `.pbix` via Power BI Desktop**:
> Microsoft Power BI `.pbix` files are proprietary, compressed binary containers that package a local VertiPaq columnar database engine, tabular mashups, and UI visual layout JSON. Microsoft does not provide a headless command-line tool to construct valid `.pbix` files without launching Power BI Desktop.
> 
> Rather than creating a misleading, corrupted binary mock-up, we have engineered:
> 1. Complete, validated source CSV files in `data/processed/`.
> 2. An automated Star Schema relational model.
> 3. Production-tested DAX analytical measures in [dax_measures.md](file:///c:/Users/USER/Documents/RetailPulse/powerbi/dax_measures.md).
> 4. Exact visual blueprints in [dashboard_design.md](file:///c:/Users/USER/Documents/RetailPulse/powerbi/dashboard_design.md).
> 5. The click-by-click instructions below to assemble the finished report in **~15–20 minutes**.

---

## 2. Prerequisites & Environment Check

1. **Power BI Desktop** is already installed on your machine (`PBIDesktopStore.exe` from the Microsoft Store).
2. All 5 Star Schema CSV files are generated and waiting in your project folder:
   - `c:\Users\USER\Documents\RetailPulse\data\processed\fact_sales.csv`
   - `c:\Users\USER\Documents\RetailPulse\data\processed\dim_date.csv`
   - `c:\Users\USER\Documents\RetailPulse\data\processed\dim_customer.csv`
   - `c:\Users\USER\Documents\RetailPulse\data\processed\dim_product.csv`
   - `c:\Users\USER\Documents\RetailPulse\data\processed\dim_geography.csv`

---

## 3. Step-by-Step Build Instructions

### Step 1: Launch Power BI Desktop & Ingest the Star Schema
1. Press the Windows key, search for **Power BI Desktop**, and press **Enter**.
2. If a splash screen appears, click the **X** in the top-right corner to close it.
3. On the **Home** ribbon, click **Get Data** > **Text/CSV**.
4. Browse to: `C:\Users\USER\Documents\RetailPulse\data\processed\`
5. Select **`fact_sales.csv`** and click **Open**.
6. In the preview window, confirm the data looks tabular and click **Load**.
7. Repeat this process for the remaining 4 dimension files:
   - `dim_date.csv`
   - `dim_customer.csv`
   - `dim_product.csv`
   - `dim_geography.csv`
8. After loading all 5 files, you will see all five tables listed on the right in the **Data** pane.

---

### Step 2: Establish Star Schema Relationships (Model View)
1. On the far-left navigation bar, click the **Model View** icon (the third icon down, showing three connected boxes).
2. Arrange your tables on the canvas:
   - Place **`fact_sales`** in the center.
   - Place **`dim_date`**, **`dim_customer`**, **`dim_product`**, and **`dim_geography`** around the fact table in a star pattern.
3. Verify or create the four 1-to-Many (`1:*`) relationships by dragging the primary key from each dimension onto the corresponding foreign key in `fact_sales`:
   - Drag `dim_date[date_key]` -> `fact_sales[date_key]`
   - Drag `dim_customer[customer_id]` -> `fact_sales[customer_id]`
   - Drag `dim_product[stock_code]` -> `fact_sales[stock_code]`
   - Drag `dim_geography[country_key]` -> `fact_sales[country_key]`
4. **Relationship Check**:
   - Double-click each connecting line.
   - Ensure **Cardinality** is **One to Many (1:*)** (Dimension to Fact).
   - Ensure **Cross filter direction** is **Single**.
   - Click **OK**.

---

### Step 3: Configure the Date Dimension & Calendar Sort Orders
1. Switch back to **Table View** or **Report View**.
2. Right-click the **`dim_date`** table in the Data pane -> Select **Mark as date table** -> **Mark as date table**.
3. In the dropdown, choose **`order_date`** -> Click **OK**.
4. **Fix Chronological Sorting**:
   - Click on the column **`month_name`** in `dim_date`.
   - In the top ribbon, click **Column tools** -> Click **Sort by column** -> Choose **`month`**.
     *(This ensures January, February, etc., sort chronologically instead of alphabetically).*
   - Click on **`day_name`** -> Click **Sort by column** -> Choose **`day_of_week`**.
   - Click on **`year_quarter`** -> Click **Sort by column** -> Choose **`date_key`**.

---

### Step 4: Create the Dedicated `_Measures` Table
Best practice in Power BI is to house all analytical calculations in a dedicated measure table:
1. On the **Home** ribbon, click **Enter Data**.
2. In the popup window, change the name from `Table1` to **`_Measures`** (with an underscore so it appears at the very top of your Data pane).
3. Click **Load**.
4. Now add your measures by right-clicking **`_Measures`** -> Select **New Measure**, then paste each formula from [dax_measures.md](file:///c:/Users/USER/Documents/RetailPulse/powerbi/dax_measures.md).

#### Core Starter Measures to Create:
```dax
Net Revenue = SUM(fact_sales[line_total])
```
*(Select measure -> Set formatting to Currency: `£`, 2 decimal places).*

```dax
Gross Sales = CALCULATE(SUM(fact_sales[line_total]), fact_sales[is_return] = 0)
```

```dax
Return Value = CALCULATE(SUM(fact_sales[line_total]), fact_sales[is_return] = 1)
```

```dax
Total Orders = DISTINCTCOUNT(fact_sales[invoice_no])
```

```dax
Average Order Value (AOV) = DIVIDE([Gross Sales], CALCULATE(DISTINCTCOUNT(fact_sales[invoice_no]), fact_sales[is_return] = 0), 0)
```

```dax
Return Rate % = DIVIDE(ABS([Return Value]), [Gross Sales], 0)
```
*(Select measure -> Set formatting to Percentage: `%`, 2 decimal places).*

```dax
Previous Month Net Sales = CALCULATE([Net Revenue], PREVIOUSMONTH(dim_date[order_date]))
```

```dax
Month-over-Month (MoM) Growth % = DIVIDE([Net Revenue] - [Previous Month Net Sales], [Previous Month Net Sales], 0)
```

```dax
Registered Customers = CALCULATE(DISTINCTCOUNT(fact_sales[customer_id]), fact_sales[customer_id] <> -1)
```

```dax
Guest Revenue Contribution % = DIVIDE(CALCULATE([Net Revenue], fact_sales[customer_id] = -1), [Net Revenue], 0)
```

```dax
Repeat Customer Rate % = DIVIDE(CALCULATE(COUNTROWS(FILTER(dim_customer, dim_customer[customer_id] <> -1 && dim_customer[total_orders] > 1))), [Registered Customers], 0)
```

---

### Step 5: Construct the 4 Report Pages

At the bottom of the canvas, click the **+** button to create 4 tabs and rename them:
1. `Executive Overview`
2. `Sales Performance`
3. `Customer Intelligence`
4. `Returns & Insights`

#### Page 1: Executive Overview
1. **Header Banner**: Insert a Shape (Rectangle) across the top, fill with `#0F172A`. Add a Text box with white text: *"RetailPulse — Executive Overview"*.
2. **Slicers**:
   - Add a Slicer visual -> Drag `dim_date[order_date]` (Between slider).
   - Add a Slicer visual -> Drag `dim_geography[market_region]` (Dropdown).
3. **KPI Cards (Top Row)**:
   - Insert a Card visual -> Field: `[Net Revenue]` (£9.75M).
   - Insert a Card visual -> Field: `[Gross Sales]` (£10.64M).
   - Insert a Card visual -> Field: `[Total Orders]` (23,796).
   - Insert a Card visual -> Field: `[Average Order Value (AOV)]` (£528.51).
4. **Visual 1 — Monthly Net Revenue Trend**:
   - Visual Type: **Line and Clustered Column Chart**.
   - Shared X-Axis: `dim_date[year_month]`.
   - Column Y-Axis: `[Gross Sales]`.
   - Line Y-Axis: `[Net Revenue]`.
5. **Visual 2 — Top 10 Revenue Products**:
   - Visual Type: **Clustered Bar Chart** (Horizontal).
   - Y-Axis: `dim_product[description]`.
   - X-Axis: `[Net Revenue]`.
   - Filters pane on this visual -> Top N -> Show Top 10 by `[Net Revenue]`.
6. **Visual 3 — Regional Revenue Share**:
   - Visual Type: **Donut Chart**.
   - Legend: `dim_geography[market_region]`.
   - Values: `[Net Revenue]`.
7. **Visual 4 — Country Revenue Treemap**:
   - Visual Type: **Treemap**.
   - Category: `dim_geography[country]`.
   - Values: `[Net Revenue]`.

#### Page 2: Sales Performance
1. Top Cards: `[Total Units Sold]` (5.57M), `[Sales Orders]` (20,136), `[Average Items per Order]` (276.7).
2. **Matrix Table**:
   - Rows: `dim_date[year]`, `dim_date[quarter]`, `dim_date[month_name]`.
   - Values: `[Gross Sales]`, `[Return Value]`, `[Net Revenue]`, `[Month-over-Month (MoM) Growth %]`.
3. **Product Volume vs Unit Price Scatter**:
   - X-Axis: `dim_product[avg_unit_price]`.
   - Y-Axis: `[Total Units Sold]`.
   - Size: `[Net Revenue]`.
4. **Day of Week Purchasing Behavior**:
   - Clustered Column Chart: X-Axis = `dim_date[day_name]`, Y-Axis = `[Net Revenue]`.
5. **Country Sales Table**:
   - Table with `dim_geography[country]`, `[Sales Orders]`, `[Net Revenue]`, `[AOV]`. Apply Data Bars to `[Net Revenue]`.

#### Page 3: Customer Intelligence
1. Top Cards: `[Registered Customers]` (4,371), `[Repeat Customer Rate %]` (69.98%), `[Guest Revenue Contribution %]` (15.08%), `[Average Spend per Registered Customer]` (£1,893.96).
2. **Monthly New vs Returning Customer Spend**:
   - Stacked Column Chart: X-Axis = `dim_date[year_month]`, Values = `[Net Revenue]`.
3. **Customer Purchase Frequency Tiers**:
   - Donut Chart using `dim_customer[loyalty_tier]` (1 Order, 2-5 Orders, 6-10 Orders, 10+ Orders).
4. **Top 10 VIP Registered Accounts Table**:
   - Table: `customer_id`, `country`, `total_orders`, `total_items_bought`, `total_spend`.
   - Filter to Top 10 by `total_spend`.

#### Page 4: Returns & Business Insights
1. Top Cards: `[Return Value]` (-£893.98k), `[Return Rate %]` (8.40%), `[Return Order Count]` (3,660).
2. **Monthly Refund Trend**:
   - Line Chart: X-Axis = `dim_date[year_month]`, Y-Axis = `[Return Value]`, Secondary Y-Axis = `[Return Rate %]`.
3. **Top 10 Most Returned SKUs**:
   - Horizontal Bar Chart: Y-Axis = `dim_product[description]`, X-Axis = `[Return Value]` (sorted by largest refund magnitude).
4. **Country Return Rate % Ranking**:
   - Bar Chart: Y-Axis = `dim_geography[country]`, X-Axis = `[Return Rate %]` (Highlighting Singapore 57.1% and Hong Kong 36.0%).
5. **Executive Recommendations Panel**:
   - Multi-row card or Text Card summarizing the 5 verified recommendations from [business_insights.md](file:///c:/Users/USER/Documents/RetailPulse/reports/business_insights.md).

---

### Step 6: Save Your File
1. In the top-left corner, click **File** > **Save As**.
2. Save the report inside your project repository:
   - File location: `C:\Users\USER\Documents\RetailPulse\powerbi\`
   - File name: **`RetailPulse.pbix`**
3. Click **Save**.

---

## 4. Beginner Troubleshooting & Common Mistakes

| Issue Observed | Root Cause | Exact Solution |
| :--- | :--- | :--- |
| **Month names sort alphabetically** (April, August, Dec...) | Default text sorting | Select `month_name` in `dim_date` -> Column tools -> **Sort by column** -> Select **`month`**. |
| **Relationship is dotted / inactive** | Multiple paths between tables | Double-click the relationship line, uncheck "Make this relationship active" on duplicates, or ensure single-direction filters. |
| **Returns showing as positive numbers** | Absolute values used everywhere | Keep `[Return Value]` negative for accounting transparency. Use `ABS()` strictly inside `[Return Rate %]`. |
| **Guest checkout rows causing blank customer names** | Missing customer ID in fact | Use `customer_id = -1` mapping to `dim_customer` guest row. |
| **Division by zero error (`#VALUE!`)** | Slash operator used (`/`) | Always use `DIVIDE(numerator, denominator, 0)` in DAX. |
