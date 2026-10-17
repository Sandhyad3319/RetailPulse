# RetailPulse: Power BI Dashboard Visual Design & Blueprint

This document specifies the exact visual components, grid coordinates, field mappings, DAX measures, formatting tokens, and user interactions for all **four coordinated pages** of the **RetailPulse** dashboard.

---

## 1. Visual Design System & Brand Palette

To ensure an executive-ready, portfolio-grade presentation, all pages adhere to a curated modern business intelligence theme:

| Element | Hex Code | Purpose & Usage |
| :--- | :--- | :--- |
| **Canvas Background** | `#F8FAFC` (Slate 50) | Clean, distraction-free neutral canvas |
| **Card / Surface Background** | `#FFFFFF` (Pure White) | Visual container with 1px border (`#E2E8F0`) and subtle drop-shadow |
| **Primary Brand Header** | `#0F172A` (Slate 900) | Top navigation banner, primary metric titles, bold typography |
| **Accent Primary / Trend** | `#0284C7` (Sky/Teal 600) | Primary line chart series, selected filter states |
| **Positive Growth / Sales** | `#10B981` (Emerald 500) | Positive sales bars, MoM growth indicators |
| **Returns / Cancellations** | `#EF4444` (Rose/Red 500) | Refund streams, return rate alerts, credit notes |
| **Secondary Accent** | `#6366F1` (Indigo 500) | Category breakdowns, customer loyalty segments |
| **Muted Text / Axis Labels** | `#64748B` (Slate 500) | Axis tick labels, subtitle annotations, secondary metadata |

- **Canvas Dimensions**: 16:9 Widescreen (`1280 x 720 px` or `1920 x 1080 px`).
- **Typography**: Segoe UI (Standard across Microsoft enterprise ecosystems).
  - Page Titles: 20pt, Bold, `#0F172A`
  - Visual Titles: 12pt, Semibold, `#1E293B`
  - KPI Callout Values: 26pt, Bold, `#0F172A`
  - Axis Labels & Legends: 9pt, Regular, `#64748B`

---

## 2. Page 1 — Executive Overview

**Objective**: Provide senior leadership with an immediate snapshot of top-line revenue, order health, monthly momentum, and geographic market share.

```text
+---------------------------------------------------------------------------------------------------+
|  RetailPulse — Executive Overview                           [ Date Slicer ] [ Region Slicer ]      |
+---------------------------------------------------------------------------------------------------+
| [ Net Revenue ]       | [ Gross Sales ]       | [ Total Orders ]      | [ Avg Order Value ]       |
|   £9.75M              |   £10.64M             |   23,796              |   £528.51                 |
+-----------------------------------------------+---------------------------------------------------+
| Visual 1: Monthly Net Revenue & Refund Trend  | Visual 2: Top 10 Revenue Products                 |
| (Line & Clustered Column: Revenue vs Refunds) | (Horizontal Bar Chart: StockCode & Name)          |
+-----------------------------------------------+---------------------------------------------------+
| Visual 3: Revenue by Market Region            | Visual 4: Geographic Revenue Distribution         |
| (Donut Chart: Domestic UK vs EU vs Export)    | (Filled Map or Treemap by Country)                |
+-----------------------------------------------+---------------------------------------------------+
```

### Visual Specifications for Page 1:
1. **Top Slicers** (X: 820, Y: 15, W: 440, H: 45):
   - Slicer 1: `dim_date[order_date]` (Between date range picker).
   - Slicer 2: `dim_geography[market_region]` (Dropdown menu).
2. **KPI Card 1 — Net Revenue** (X: 20, Y: 70, W: 295, H: 90):
   - Measure: `[Net Revenue]`, Format: Currency (`£#,##0.00`), Callout: 24pt Bold.
3. **KPI Card 2 — Gross Sales** (X: 335, Y: 70, W: 295, H: 90):
   - Measure: `[Gross Sales]`, Format: Currency (`£#,##0.00`), Subtitle: "Pre-refund revenue".
4. **KPI Card 3 — Total Orders** (X: 650, Y: 70, W: 295, H: 90):
   - Measure: `[Total Orders]`, Format: Whole Number (`#,##0`).
5. **KPI Card 4 — Average Order Value** (X: 965, Y: 70, W: 295, H: 90):
   - Measure: `[Average Order Value (AOV)]`, Format: Currency (`£#,##0.00`).
6. **Visual 1 — Monthly Net Revenue & Return Trend** (X: 20, Y: 180, W: 610, H: 260):
   - Visual Type: **Line and Clustered Column Chart**
   - Shared X-Axis: `dim_date[year_month]`
   - Column Y-Axis: `[Gross Sales]` (Color: `#0284C7`)
   - Line Y-Axis: `[Net Revenue]` (Color: `#10B981`, Stroke: 3px)
   - Secondary Line: `[Return Value]` (Color: `#EF4444`, Stroke: 2px, Dashed)
7. **Visual 2 — Top 10 Products by Net Revenue** (X: 650, Y: 180, W: 610, H: 260):
   - Visual Type: **Clustered Bar Chart** (Horizontal)
   - Y-Axis: `dim_product[description]` (Top 10 filter by `[Net Revenue]`)
   - X-Axis: `[Net Revenue]`
   - Data Labels: On (`£#,##0K`), Bar Color: `#0284C7`
8. **Visual 3 — Revenue Share by Market Region** (X: 20, Y: 460, W: 450, H: 240):
   - Visual Type: **Donut Chart**
   - Legend: `dim_geography[market_region]`
   - Values: `[Net Revenue]`
   - Colors: Domestic UK (`#0284C7`), EU (`#10B981`), International Export (`#6366F1`)
   - Detail Labels: Category, Percent of total
9. **Visual 4 — Country Revenue Treemap** (X: 490, Y: 460, W: 770, H: 240):
   - Visual Type: **Treemap**
   - Category: `dim_geography[country]`
   - Values: `[Net Revenue]`
   - Tooltip: `[Total Orders]`, `[Return Rate %]`

---

## 3. Page 2 — Sales Performance

**Objective**: Deep-dive into sales volume, order frequency, price elasticity, and product portfolio contribution.

```text
+---------------------------------------------------------------------------------------------------+
|  RetailPulse — Sales Performance                            [ Year-Quarter Slicer ] [ SKU Search ] |
+---------------------------------------------------------------------------------------------------+
| [ Total Units Sold ]  | [ Completed Sales ]   | [ Items / Order ]     | [ Active Trading Days ]   |
|   5.57M Units         |   20,136 Orders       |   276.7 Units         |   305 Days                |
+-----------------------------------------------+---------------------------------------------------+
| Visual 1: Quarterly Sales Performance Matrix  | Visual 2: Product Volume vs Unit Price Scatter    |
| (Quarter, Month, Revenue, Units, Growth %)    | (X: Avg Unit Price, Y: Units Sold, Size: Revenue) |
+-----------------------------------------------+---------------------------------------------------+
| Visual 3: Day-of-Week Purchasing Patterns     | Visual 4: Top 15 Country Revenue & Volume Matrix  |
| (Column Chart: Monday – Sunday Net Sales)     | (Country, Orders, Gross Sales, Returns, Net)      |
+-----------------------------------------------+---------------------------------------------------+
```

### Visual Specifications for Page 2:
1. **Top Slicers**:
   - Slicer 1: `dim_date[year_quarter]` (Tile buttons).
   - Slicer 2: `dim_product[description]` (Dropdown search).
2. **KPI Cards (Units, Sales Orders, Items/Order, Trading Days)**:
   - Measures: `[Total Units Sold]`, `[Sales Orders]`, `[Average Items per Order]`, `DISTINCTCOUNT(fact_sales[date_key])`.
3. **Visual 1 — Monthly & Quarterly Performance Matrix** (X: 20, Y: 180, W: 610, H: 260):
   - Visual Type: **Matrix**
   - Rows: `dim_date[year]`, `dim_date[quarter]`, `dim_date[month_name]`
   - Values: `[Gross Sales]`, `[Return Value]`, `[Net Revenue]`, `[Month-over-Month (MoM) Growth %]`
   - Conditional Formatting: Background color on `[Month-over-Month (MoM) Growth %]` (Red to Green divergency).
4. **Visual 2 — Product Price Elasticity Scatter Plot** (X: 650, Y: 180, W: 610, H: 260):
   - Visual Type: **Scatter Chart**
   - Details: `dim_product[stock_code]`
   - X-Axis: `dim_product[avg_unit_price]` (Max £30 to eliminate outlier postal fees)
   - Y-Axis: `[Total Units Sold]`
   - Size: `[Net Revenue]`
   - Tooltip: `dim_product[description]`
5. **Visual 3 — Day of Week Sales Pattern** (X: 20, Y: 460, W: 450, H: 240):
   - Visual Type: **Clustered Column Chart**
   - X-Axis: `dim_date[day_name]` (Sorted by `dim_date[day_of_week]`)
   - Y-Axis: `[Net Revenue]`
   - Data Labels: On
6. **Visual 4 — Country Performance Table** (X: 490, Y: 460, W: 770, H: 240):
   - Visual Type: **Table**
   - Columns: `dim_geography[country]`, `dim_geography[market_region]`, `[Sales Orders]`, `[Net Revenue]`, `[Average Order Value (AOV)]`
   - Data Bars: Applied to `[Net Revenue]` column

---

## 4. Page 3 — Customer Intelligence

**Objective**: Uncover customer acquisition dynamics, retention rates, guest checkout risks, and VIP customer account value.

```text
+---------------------------------------------------------------------------------------------------+
|  RetailPulse — Customer Intelligence                        [ Customer Type ] [ Country Slicer ]   |
+---------------------------------------------------------------------------------------------------+
| [ Registered Accounts]| [ Repeat Customer Rate| [ Guest Revenue Share | [ Avg Spend / Customer ]  |
|   4,371 Accounts      |   69.98%              |   15.08% (£1.47M)     |   £1,893.96               |
+-----------------------------------------------+---------------------------------------------------+
| Visual 1: Monthly New vs Returning Spend      | Visual 2: Purchase Frequency Loyalty Tiers        |
| (Stacked Bar: First-time vs Returning cohorts)| (Donut Chart: 1 Order, 2-5, 6-10, 10+ Orders)     |
+-----------------------------------------------+---------------------------------------------------+
| Visual 3: Top 10 Registered VIP Accounts      | Visual 4: Customer Account Tenure & Spend Matrix  |
| (Customer ID, Country, Orders, Lifetime Spend)| (Decile breakdown of registered customer base)    |
+-----------------------------------------------+---------------------------------------------------+
```

### Visual Specifications for Page 3:
1. **Top Slicers**:
   - Slicer 1: `dim_customer[customer_type]` (Registered vs Guest Checkout).
   - Slicer 2: `dim_geography[country]` (Dropdown).
2. **KPI Cards (Registered Accounts, Repeat Rate, Guest Share, Avg Spend)**:
   - Measures: `[Registered Customers]`, `[Repeat Customer Rate %]`, `[Guest Revenue Contribution %]`, `[Average Spend per Registered Customer]`.
3. **Visual 1 — New vs Returning Customer Monthly Spend** (X: 20, Y: 180, W: 610, H: 260):
   - Visual Type: **Stacked Column Chart**
   - X-Axis: `dim_date[year_month]`
   - Legend: Calculation / Field: `buyer_status` (New Customer vs Returning Customer)
   - Y-Axis: `[Net Revenue]`
   - Colors: Returning (`#0284C7`), New (`#10B981`)
4. **Visual 2 — Customer Purchase Frequency Distribution** (X: 650, Y: 180, W: 610, H: 260):
   - Visual Type: **Donut Chart**
   - Legend: `dim_customer[loyalty_tier]` (1 Order, 2-5 Orders, 6-10 Orders, 10+ Orders)
   - Values: Count of `customer_id`
   - Colors: 1 Order (`#94A3B8`), 2-5 Orders (`#38BDF8`), 6-10 Orders (`#0284C7`), 10+ Orders (`#0F172A`)
5. **Visual 3 — Top 10 VIP Registered Customer Accounts** (X: 20, Y: 460, W: 680, H: 240):
   - Visual Type: **Table**
   - Columns: `dim_customer[customer_id]`, `dim_customer[country]`, `dim_customer[total_orders]`, `dim_customer[total_items_bought]`, `dim_customer[total_spend]`
   - Filter: Top 10 by `dim_customer[total_spend]`
6. **Visual 4 — Guest vs Registered Split Comparison** (X: 720, Y: 460, W: 540, H: 240):
   - Visual Type: **Clustered Bar Chart**
   - Y-Axis: `dim_customer[customer_type]`
   - X-Axis: `[Net Revenue]` and `[Total Orders]`
   - Tooltip: `[Guest Revenue Contribution %]`

---

## 5. Page 4 — Returns & Business Insights

**Objective**: Address product return friction, evaluate cancellation severity by country, and communicate evidence-backed recommendations to management.

```text
+---------------------------------------------------------------------------------------------------+
|  RetailPulse — Returns & Strategic Insights                 [ Market Region ] [ Product Filter ]  |
+---------------------------------------------------------------------------------------------------+
| [ Return Refund Total]| [ Return Rate % ]     | [ Cancelled Invoices ]| [ Net Revenue Saved ]     |
|   -£893,979.73        |   8.40%               |   3,660 Return Orders |   £9.75M Clean Revenue    |
+-----------------------------------------------+---------------------------------------------------+
| Visual 1: Monthly Return Value & Rate Trend   | Visual 2: Top 10 Most Returned SKUs               |
| (Line Chart: Refund £ and Return Rate %)      | (Bar Chart: Product Description & Refund Amount)  |
+-----------------------------------------------+---------------------------------------------------+
| Visual 3: Return Rate % by Country Market     | Visual 4: Executive Insights & Strategy Panel     |
| (Highlights Singapore 57%, Hong Kong 36%)     | (5 Data-Backed Discoveries & Action Plan)         |
+-----------------------------------------------+---------------------------------------------------+
```

### Visual Specifications for Page 4:
1. **KPI Cards (Refund Total, Return Rate %, Return Orders)**:
   - Measures: `[Return Value]` (Color `#EF4444`), `[Return Rate %]`, `[Return Order Count]`.
2. **Visual 1 — Monthly Return Value Trend** (X: 20, Y: 180, W: 610, H: 260):
   - Visual Type: **Line Chart**
   - X-Axis: `dim_date[year_month]`
   - Y-Axis: `[Return Value]`
   - Secondary Y-Axis: `[Return Rate %]`
   - Colors: Line `#EF4444`
3. **Visual 2 — Top 10 Most Returned Products by Refund Value** (X: 650, Y: 180, W: 610, H: 260):
   - Visual Type: **Clustered Bar Chart** (Horizontal)
   - Y-Axis: `dim_product[description]` (Filtered by `is_return = 1`)
   - X-Axis: `[Return Value]`
   - Bar Color: `#EF4444`
4. **Visual 3 — Country Return Rate % Ranking** (X: 20, Y: 460, W: 550, H: 240):
   - Visual Type: **Clustered Bar Chart**
   - Y-Axis: `dim_geography[country]` (Countries with > £10k gross sales)
   - X-Axis: `[Return Rate %]`
   - Alert Threshold: Highlight bars over 20% in dark crimson (Singapore 57.1%, Hong Kong 36.0%)
5. **Visual 4 — Executive Strategic Recommendations Card** (X: 590, Y: 460, W: 670, H: 240):
   - Visual Type: **Multi-row Card or Text Card**
   - Bullet 1: **Q4 Peak Preparedness**: Allocate stock buffer 6 weeks ahead of Nov peak (+194% volume).
   - Bullet 2: **VIP Wholesale Concierge**: Top 10% VIPs drive 55.9% of spend. Establish direct accounts.
   - Bullet 3: **Export Packaging Overhaul**: Singapore/Hong Kong returns >35% signal transit/customs friction.
   - Bullet 4: **Guest Account Capture**: £1.47M (15.1%) in guest baskets; offer £10 post-checkout incentive.
