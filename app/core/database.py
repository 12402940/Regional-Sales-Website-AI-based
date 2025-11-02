import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/sales.db")

def get_connection():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    """Create sales table if not exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT,
            product TEXT,
            quantity INTEGER,
            price REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Database & tables created successfully.")
