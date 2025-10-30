
import psycopg2
import pandas as pd
import os
import logging
from datetime import datetime

# Logging Setup 
log_folder = r"D:\Vendor performance\logs" # Ensure this folder exists
os.makedirs(log_folder, exist_ok=True) 


today = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(log_folder, f"db_load_{today}.txt")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("--------------------------------------------------")
logging.info(f"RUN START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("--------------------------------------------------")


#  Database Connection
def db_connection():
    try:
        conn = psycopg2.connect(
            host="your_host",
            database="your_database",
            user="your_username",
            password="your_password",
            port="your_port"
        )
        print(" Database connection successful")
        logging.info(" Database connection successful.")
        return conn
    except Exception as e:
        logging.error(f" Database connection failed: {e}")
        raise


#  Guess PostgreSQL Data Types 
def map_dtype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    else:
        return "TEXT"


# Create Table if Missing 
def create_table_if_not_exists(conn, df, table_name):
    try:
        cur = conn.cursor()
        columns = ', '.join([f'"{col}" {map_dtype(df[col].dtype)}' for col in df.columns])
        cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')
        conn.commit()
        cur.close()
        logging.info(f" Table '{table_name}' created or already exists.")
    except Exception as e:
        logging.error(f" Error creating table '{table_name}': {e}")


#  Load CSV Data into Table 
def load_to_db(conn, file_path, table_name):
    try:
        cur = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as f:
            cur.copy_expert(f'COPY "{table_name}" FROM STDIN WITH CSV HEADER DELIMITER \',\'', f)
        conn.commit()
        cur.close()
        print(f" {table_name} loaded successfully!")
        logging.info(f"Data loaded successfully into '{table_name}'.")
    except Exception as e:
        logging.error(f" Error loading data into '{table_name}': {e}")


# Main Script 
data_folder = r"D:\Vendor performance\data\data"

try:
    conn = db_connection()
    for file in os.listdir(data_folder):
        if file.endswith('.csv'):
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)
            table_name = os.path.splitext(file)[0].lower()

            create_table_if_not_exists(conn, df, table_name)
            load_to_db(conn, file_path, table_name)

    conn.close()
    print("All CSV files loaded successfully!")
    logging.info(" All CSV files loaded successfully.")
except Exception as e:
    logging.error(f" Script failed: {e}")

logging.info("--------------------------------------------------")
logging.info(f"RUN END: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("--------------------------------------------------\n")




