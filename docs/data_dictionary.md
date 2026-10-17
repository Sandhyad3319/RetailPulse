# RetailPulse: Data Dictionary & Data Source Specification

## 1. Dataset Overview & Source Citation

| Metadata Field | Description |
| :--- | :--- |
| **Project Name** | **RetailPulse — Sales & Customer Intelligence Analytics Platform** |
| **Dataset Title** | **Online Retail Dataset** |
| **Repository** | University of California, Irvine (UCI) Machine Learning Repository |
| **Dataset URL** | [https://archive.ics.uci.edu/dataset/352/online+retail](https://archive.ics.uci.edu/dataset/352/online+retail) |
| **DOI / Identifier** | UCI Dataset ID: 352 |
| **Data Provider** | Dr. Daqing Chen, Director of Public Analytics group, London South Bank University |
| **Time Period Covered** | **01/12/2010 to 09/12/2011** (1 year and 9 days) |
| **License** | [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) |
| **Citation** | Chen, D., Sain, S. L., & Guo, K. (2012). *Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining*. Journal of Database Marketing & Customer Strategy Management, 19(3), 197–208. |
| **Business Context** | A UK-based, registered non-store online retail business specializing in unique all-occasion giftware. A substantial portion of the customer base consists of small businesses and wholesalers. |

---

## 2. Raw Data Dictionary

The raw dataset contains **541,909 rows** and **8 columns**. The table below details every field:

| Column Name | Business Description | Raw Data Type | Target Analytical Type | Nullable? | Example Values | Validation Rules & Behavioral Constraints |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `InvoiceNo` | Unique identifier for a sales transaction or order | String / Object | `VARCHAR(20)` | No | `536365`, `C536379`, `581587` | 6-digit integral number. If the code begins with letter **'C'** or **'c'**, it explicitly indicates an **order cancellation or customer return**. |
| `StockCode` | Product (item) SKU code | String / Object | `VARCHAR(20)` | No | `85123A`, `71053`, `POST`, `M` | Typically a 5-digit number, occasionally followed by a letter suffix. Also contains non-inventory codes like `POST` (postage), `M` (manual entry), `D` (discount), and `BANK CHARGES`. |
| `Description` | Product name and item title | String / Object | `VARCHAR(255)` | Yes (1,454 nulls) | `WHITE HANGING HEART T-LIGHT HOLDER` | Free-text merchandise description. Missing values correlate with inventory adjustments, damaged goods, or system testing. |
| `Quantity` | Units of product sold or returned per transaction line | Integer / Float | `INTEGER` | No | `6`, `24`, `-1`, `-80995` | **Positive values** = items purchased. **Negative values** = items returned, orders cancelled, or inventory write-offs. |
| `InvoiceDate` | Date and timestamp when the transaction was logged | String / Datetime | `DATETIME` | No | `2010-12-01 08:26:00` | Format: `YYYY-MM-DD HH:MM:SS`. Used to derive calendar dimensions (`Year`, `Quarter`, `Month`, `DayOfWeek`). |
| `UnitPrice` | Price per unit of product in British Pounds Sterling (£) | Float / Numeric | `DECIMAL(10,2)` | No | `2.55`, `3.39`, `0.00` | Stated in GBP (£). Zero values indicate free items or non-commercial adjustments. Rare negative entries represent debt adjustments. |
| `CustomerID` | Unique 5-digit identifier assigned to each registered customer | Float / String | `INTEGER` / `VARCHAR(20)` | Yes (135,080 nulls) | `17850`, `13047`, `12583` | Nominal 5-digit customer identifier. Missing in ~24.9% of records (unregistered / guest checkouts). |
| `Country` | Name of the nation where the customer resides | String / Object | `VARCHAR(100)` | No | `United Kingdom`, `Germany`, `France` | Country name for geographic distribution. United Kingdom accounts for >90% of total transactions. |

---

## 3. Critical Analytical Assumptions & Dataset Limitations

To maintain the highest standards of professional data integrity, the following limitations are explicitly documented:

### 1. Absence of Cost, Profit & Margin Data
- **Source Truth**: The UCI Online Retail dataset **does not contain product unit cost, shipping cost, tax rate, or profit margins**.
- **Governance Rule**: In this project, we **never invent, assume, or fabricate costs or profit margins**. All financial metrics are strictly reported as **Gross Sales**, **Returns**, and **Net Revenue** (`Quantity * UnitPrice`). Any separate scenario demonstrating profit modeling must be distinctly labeled as a demonstration scenario.

### 2. Treatment of Missing Customer IDs (Registered vs. Guest Checkouts)
- Approximately **24.9% of transactions** (135,080 rows) have a missing `CustomerID`.
- **Business Rationale**: In modern e-commerce, customers are frequently allowed to complete purchases without logging into an account ("Guest Checkout").
- **Analytical Rule**:
  - For **Total Sales, Revenue, Product Rankings, and Geographic Analysis**, guest transactions are **retained** because they represent genuine corporate revenue.
  - For **Customer Retention, Repeat Purchase Rate, and Customer Lifetime Value (CLV)**, analysis is filtered to the **registered customer cohort** where `CustomerID` is reliably tracked.

### 3. Cancellations vs. Internal Adjustments
- Rows with an `InvoiceNo` starting with **'C'** and negative quantities are verified **customer cancellations / returns**. They are assigned a flag `IsReturn = True`.
- Rows with negative quantities but **no 'C'** and missing customer IDs are **internal inventory adjustments** (damaged goods, lost stock, administrative write-offs) and are filtered out of consumer sales metrics during Phase 3 cleaning.

### 4. Currency
- All monetary amounts are denominated in **British Pounds Sterling (£ / GBP)**.
