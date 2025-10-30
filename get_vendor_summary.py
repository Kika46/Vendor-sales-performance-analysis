import pandas as pd
import psycopg2
import logging
import os
from datetime import datetime
from Main_file import create_table_if_not_exists, load_to_db

# Proper logging setup
logging.basicConfig(
    filename="D:\\Vendor performance\\logs\\get_vendor_summary.log",  # Log file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

# SQL Query Function
def create_vendor_summary(conn):
    logging.info("Starting vendor summary SQL query...")
    query = """
    WITH FreightSummary AS (
        SELECT "VendorNumber", SUM("Freight") AS Total_Freight
        FROM vendor_invoice
        GROUP BY "VendorNumber"
    ),
    PurchaseSummary AS (
        SELECT p."VendorNumber", p."VendorName", p."Brand", p."Description",
               p."PurchasePrice", pp."Volume", pp."Price" AS "actualPrice",
               SUM(p."Quantity") AS TotalQuantity,
               SUM(p."Dollars") AS TotalPurchaseDollars
        FROM purchases p
        JOIN purchase_prices pp ON pp."Brand" = p."Brand"
        WHERE p."PurchasePrice" > 0
        GROUP BY p."VendorNumber", p."VendorName", p."Brand", p."Description", 
                 p."PurchasePrice", pp."Volume", pp."Price"
    ),
    SalesSummary AS (
        SELECT "VendorNo" AS "VendorNumber", "Brand",
               SUM("SalesPrice") AS TotalSalesPrice,
               SUM("SalesQuantity") AS TotalSalesQuantity,
               SUM("SalesDollars") AS TotalSalesDollars,
               SUM("ExciseTax") AS TotalExciseTax
        FROM sales
        GROUP BY "VendorNo", "Brand"
    )
    SELECT ps."VendorNumber", ps."VendorName", ps."Brand", ps."Description",
           ps."PurchasePrice", ps."Volume", ps."actualPrice",
           ps.TotalQuantity, ps.TotalPurchaseDollars,
           ss.TotalSalesPrice, ss.TotalSalesQuantity, ss.TotalSalesDollars, ss.TotalExciseTax,
           fs.Total_Freight
    FROM PurchaseSummary ps
    LEFT JOIN SalesSummary ss ON ps."VendorNumber" = ss."VendorNumber" AND ps."Brand" = ss."Brand"
    LEFT JOIN FreightSummary fs ON ps."VendorNumber" = fs."VendorNumber"
    ORDER BY ss.TotalSalesDollars DESC;
    """
    chunks = []
    for chunk in pd.read_sql_query(query, conn, chunksize=50000):
        chunks.append(chunk)
        logging.info(f"Fetched {len(chunk)} rows in a chunk")
    df = pd.concat(chunks, ignore_index=True)
    logging.info(f"Total {len(df)} rows fetched")
    return df


# Data Cleaning and Calculations
def clean_data(df):
    logging.info("Starting data cleaning...")
    df = df.fillna(0)
    df.columns = df.columns.str.lower()

    df["volume"] = df["volume"].astype(float)
    df["vendorname"] = df["vendorname"].str.strip()
    df["description"] = df["description"].str.strip()

    # Calculations
    df["gross_profit"] = df["totalsalesdollars"] - df["totalpurchasedollars"]
    df["profit_margin"] = df.apply(
        lambda x: (x["gross_profit"] / x["totalsalesdollars"] * 100) if x["totalsalesdollars"] > 0 else 0,
        axis=1
    )
    df["stock_turnover"] = df.apply(
        lambda x: (x["totalsalesquantity"] / x["totalquantity"]) if x["totalquantity"] > 0 else 0,
        axis=1
    )
    df["sales_to_purchase_ratio"] = df.apply(
        lambda x: (x["totalsalesdollars"] / x["totalpurchasedollars"]) if x["totalpurchasedollars"] > 0 else 0,
        axis=1
    )

    logging.info("Data cleaning completed")
    return df


# Main ETL Function
def main():
    try:
        logging.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host="your_host",
            database="your_database",
            user="postgres",
            password="your_password",
            port="your_port"
        )

        # --- Extract + Transform ---
        summary_df = create_vendor_summary(conn)
        clean_df = clean_data(summary_df)

        # --- Load into PostgreSQL ---
        create_table_if_not_exists(conn, clean_df, "vendor_sales_summary")
        load_to_db(conn, clean_df, "vendor_sales_summary")

        # --- Export to Excel ---
        output_folder = r"D:\Excel output folder"
        os.makedirs(output_folder, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        excel_path = os.path.join(output_folder, f"vendor_sales_summary_{today}.xlsx")

        clean_df.to_excel(excel_path, index=False)
        logging.info(f"Data successfully saved to Excel at: {excel_path}")

        logging.info("ETL process completed successfully.")

    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        print(f"ETL process failed: {e}")

    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")


#  Run Script
if __name__ == "__main__":
    main()
