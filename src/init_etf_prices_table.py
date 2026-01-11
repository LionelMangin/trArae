"""
Script to initialize the ETF prices table in the database.
This table stores daily ETF prices fetched from the web.
"""
import sqlite3
from pathlib import Path

DB_PATH = "data/trade_republic.db"

def init_etf_prices_table():
    """Create the etf_prices table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table with unique constraint on (isin, date)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS etf_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isin TEXT NOT NULL,
            date TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(isin, date)
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_etf_prices_isin_date 
        ON etf_prices(isin, date DESC)
    """)
    
    conn.commit()
    conn.close()
    print("OK - Table etf_prices created successfully")

if __name__ == "__main__":
    init_etf_prices_table()
