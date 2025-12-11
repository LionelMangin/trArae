import sqlite3
import pandas as pd

DB_PATH = "data/trade_republic.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transactions WHERE type = 'DEPOSIT'", conn)
conn.close()

print("=== Tous les dépôts (DEPOSIT) ===")
print(f"Nombre total: {len(df)}")
print("\nNoms uniques des dépôts:")
for name in df['name'].unique():
    count = len(df[df['name'] == name])
    print(f"  - '{name}' ({count} occurrences)")
