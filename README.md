# Vendor Sales Performance Analysis

This project automates the process of extracting, transforming, and analyzing vendor sales data using **Python**, **PostgreSQL**, and **Power BI**.  
It aims to provide clear insights into vendor profitability, sales efficiency, and inventory performance through an end-to-end data analytics pipeline.

---

## 🧩 Project Overview
This project combines data engineering, exploratory analysis, and business intelligence to evaluate vendor performance and profitability.  
Using Python for ETL, PostgreSQL for structured data storage, and Power BI for visualization, the project helps identify high-performing vendors, cost-saving opportunities, and inventory inefficiencies.

---

## 💼 Business Problem
Businesses dealing with multiple vendors often struggle to track:
- Which vendors generate the most profit  
- How inventory turnover impacts profitability  
- Where inefficiencies like unsold inventory exist  

This project solves these challenges by automating data extraction (Python), storing structured data (PostgreSQL), and visualizing insights (Power BI dashboards).

---

## 🛠️ Setup Instructions

### 1️⃣ Create Database in PostgreSQL
1. Open **pgAdmin** or SQL terminal.  
2. Run the following command:
   ```sql
   CREATE DATABASE Vendors_db;

2️⃣ Run Scripts
Run Main_file.py → loads CSVs into PostgreSQL.
Run get_vendor_summary.py → cleans data, computes KPIs, and exports Excel.
🗂️ Logs and Excel outputs are saved automatically.


3️⃣ Open Power BI Dashboard
Open vendor_dashboard.pbix in Power BI Desktop.
Refresh the data to view live insights


⚙️ Tools & Technologies

Python (Pandas, Psycopg2, Logging)
PostgreSQL
Power BI
Excel / CSV
Jupyter Notebook


📈 Key Insights
198 brands show low sales but high profit margins → promotion opportunities.
Top 10 vendors contribute ~65% of total purchases → supplier concentration risk.
Bulk orders cut unit cost by ≈ 72%.
$2.7M unsold inventory identified → inventory optimization required.

