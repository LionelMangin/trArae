import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "data/trade_republic.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Get current month and year
now = datetime.now()
current_month = now.month
current_year = now.year

# Filter transactions for current month
df_current_month = df[
    (df['date'].dt.month == current_month) & 
    (df['date'].dt.year == current_year)
]

print(f"=== Mois actuel: {current_month}/{current_year} ===")
print(f"Nombre total de transactions: {len(df_current_month)}")

# Count deposits this month (type == 'DEPOSIT')
monthly_deposits = df_current_month[df_current_month['type'] == 'DEPOSIT']
monthly_deposits_count = len(monthly_deposits)
monthly_deposits_total = monthly_deposits['value'].sum() if not monthly_deposits.empty else 0

print(f"\n=== Dépôts du mois (type == 'DEPOSIT') ===")
print(f"Nombre de dépôts: {monthly_deposits_count}")
print(f"Total des dépôts: {monthly_deposits_total}€")
print("\nDétails:")
print(monthly_deposits[['date', 'name', 'type', 'value']].to_string())

# Calculate total deposits (all time)
total_deposits_df = df[df['type'] == 'DEPOSIT']
total_deposits = total_deposits_df['value'].sum() if not total_deposits_df.empty else 0

print(f"\n=== Total des dépôts (tous les temps) ===")
print(f"Nombre total: {len(total_deposits_df)}")
print(f"Montant total: {total_deposits}€")
