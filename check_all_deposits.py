import sqlite3
import pandas as pd

DB_PATH = "data/trade_republic.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transactions WHERE type = 'DEPOSIT'", conn)
conn.close()

print("=== All deposits (DEPOSIT) ===")
print(f"Total count: {len(df)}")
print("\nUnique deposit names:")
for name in df['name'].unique():
    count = len(df[df['name'] == name])
    print(f"  - '{name}' ({count} occurrences)")
