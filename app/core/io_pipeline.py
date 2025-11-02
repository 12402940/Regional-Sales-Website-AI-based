import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sales.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_sales.csv")

def init_db():
    """Ensure sales table exists, load from CSV if missing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
    exists = cursor.fetchone()

    if not exists:
        # Load from CSV
        df = pd.read_csv(CSV_PATH)
        df.to_sql("sales", conn, index=False, if_exists="replace")
        print("✅ Loaded sample_sales.csv into database")

    conn.commit()
    conn.close()

def fetch_data():
    """Fetch data from sales table."""
    init_db()  # make sure table exists
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    return df
