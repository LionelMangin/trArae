import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "data/trade_republic.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transactions WHERE date LIKE '2025-12%'", conn)
conn.close()

print("=== Transactions of December 2025 ===")
print(df[['date', 'name', 'type', 'value']].to_string())

# Check deposit pattern
deposit_pattern = 'MELLE CARLA CHAVATTE - Fertig'
print(f"\n=== Searching for pattern: '{deposit_pattern}' ===")

deposits = df[df['name'].str.contains(deposit_pattern, na=False)]
print(f"Number of deposits found: {len(deposits)}")
print(deposits[['date', 'name', 'value']].to_string())

# Check current month calculation
now = datetime.now()
print(f"\n=== Current date: {now} ===")
print(f"Current month: {now.month}")
print(f"Current year: {now.year}")

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])
df_current_month = df[
    (df['date'].dt.month == now.month) & 
    (df['date'].dt.year == now.year)
]

print(f"\n=== Transactions of current month ({now.month}/{now.year}) ===")
print(f"Total count: {len(df_current_month)}")
print(df_current_month[['date', 'name', 'type', 'value']].to_string())

monthly_deposits = df_current_month[
    df_current_month['name'].str.contains(deposit_pattern, na=False)
]
print(f"\n=== Deposits of current month ===")
print(f"Count: {len(monthly_deposits)}")
print(monthly_deposits[['date', 'name', 'value']].to_string())
