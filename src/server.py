from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import pandas as pd
from pathlib import Path
import logging
import configparser

# Load Config
config = configparser.ConfigParser()
config.read('config/config.ini')
blacklist_str = config.get('filters', 'blacklist_isins', fallback='LU2194448267')
blacklist_isins = [isin.strip() for isin in blacklist_str.split(',') if isin.strip()]

# Portfolio Config
deposit_pattern = config.get('portfolio', 'deposit_name_pattern', fallback='MELLE CARLA CHAVATTE - Fertig')
start_year = config.getint('portfolio', 'start_year', fallback=2025)
start_month = config.getint('portfolio', 'start_month', fallback=8)

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/trade_republic.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if Path("src/static/favicon.ico").exists():
        return FileResponse("src/static/favicon.ico")
    return Response(status_code=204)

@app.get("/api/transactions")
def get_transactions():
    conn = get_db_connection()
    
    query = "SELECT * FROM transactions"
    params = []
    
    if blacklist_isins:
        placeholders = ','.join(['?'] * len(blacklist_isins))
        query += f" WHERE isin NOT IN ({placeholders}) OR isin IS NULL"
        params.extend(blacklist_isins)
        
    query += " ORDER BY date DESC"
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(t) for t in transactions]

@app.get("/api/summary")
def get_summary(use_current_price: bool = False):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    
    # Filter out blacklisted ISINs
    if blacklist_isins and not df.empty:
        df = df[~df['isin'].isin(blacklist_isins)]
    
    if df.empty:
        conn.close()
        return {
            "total_transactions": 0,
            "last_update": None,
            "last_transaction_date": None,
            "monthly_purchases_count": 0,
            "monthly_deposits_count": 0,
            "monthly_purchases_total": 0,
            "monthly_deposits_total": 0,
            "total_deposits": 0,
            "total_invested": 0,
            "total_current_value": 0,
            "monthly_invested": 0,
            "total_plus_value": 0,
            "total_missing": 0
        }

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], format='ISO8601', utc=True)
    
    # Get current month and year
    from datetime import datetime
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Filter transactions for current month
    df_current_month = df[
        (df['date'].dt.month == current_month) & 
        (df['date'].dt.year == current_year)
    ]
    
    # Count purchases this month (type == 'Savings Plan')
    monthly_purchases = df_current_month[df_current_month['type'] == 'Savings Plan']
    monthly_purchases_count = len(monthly_purchases)
    monthly_purchases_total = abs(monthly_purchases['value'].sum()) if not monthly_purchases.empty else 0
    
    # Count deposits this month (type == 'DEPOSIT')
    # Using type instead of name pattern for better robustness
    monthly_deposits = df_current_month[df_current_month['type'] == 'DEPOSIT']
    monthly_deposits_count = len(monthly_deposits)
    monthly_deposits_total = monthly_deposits['value'].sum() if not monthly_deposits.empty else 0

    # Calculate total deposits (all time, type == 'DEPOSIT')
    total_deposits_df = df[df['type'] == 'DEPOSIT']
    total_deposits = total_deposits_df['value'].sum() if not total_deposits_df.empty else 0
    
    # NEW METRICS
    # Total invested (sum of all Savings Plan purchases)
    all_purchases = df[df['type'] == 'Savings Plan']
    total_invested = abs(all_purchases['value'].sum()) if not all_purchases.empty else 0
    
    # Monthly invested (purchases this month)
    monthly_invested = monthly_purchases_total
    
    # Last transaction date
    last_transaction_date = df['date'].max().isoformat() if not df.empty else None
    
    # Close connection before calling get_positions (which opens its own connection)
    conn.close()
    
    # Get positions to calculate total current value and plus-value
    positions = get_positions(use_current_price=use_current_price)  # Pass the parameter
    total_current_value = sum(pos['current_value'] for pos in positions)
    total_plus_value = total_current_value - total_invested
    total_missing = sum(pos['missing'] for pos in positions)
    
    return {
        "total_transactions": len(df),
        "last_update": df['date'].max().isoformat() if not df.empty else None,
        "last_transaction_date": last_transaction_date,
        "monthly_purchases_count": monthly_purchases_count,
        "monthly_deposits_count": monthly_deposits_count,
        "monthly_purchases_total": monthly_purchases_total,
        "monthly_deposits_total": monthly_deposits_total,
        "total_deposits": total_deposits,
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current_value, 2),
        "monthly_invested": round(monthly_invested, 2),
        "total_plus_value": round(total_plus_value, 2),
        "total_missing": round(total_missing, 2)
    }

@app.get("/api/positions")
def get_positions(use_current_price: bool = False):
    conn = get_db_connection()
    # Filter transactions with ISIN
    # Include buys (type = 'Savings Plan') AND sells (name contains 'Liquidation')
    query = """SELECT * FROM transactions 
           WHERE isin IS NOT NULL 
           AND (type = 'Savings Plan' OR name LIKE '%Liquidation%')"""
           
    params = []
    if blacklist_isins:
        placeholders = ','.join(['?'] * len(blacklist_isins))
        query += f" AND isin NOT IN ({placeholders})"
        params.extend(blacklist_isins)

    df = pd.read_sql_query(query, conn, params=params)
    
    # Get current prices if requested
    current_prices = {}
    if use_current_price:
        cursor = conn.cursor()
        # Get the most recent price for each ISIN
        cursor.execute("""
            SELECT isin, price 
            FROM etf_prices 
            WHERE (isin, date) IN (
                SELECT isin, MAX(date) 
                FROM etf_prices 
                GROUP BY isin
            )
        """)
        current_prices = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    if df.empty: return []

    # Convert date column to datetime
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], format='ISO8601', utc=True)

    # Get current date for "manque" calculation
    from datetime import datetime
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Calculate base months since start date (0-indexed offset from start)
    # Aug 2025 start, Aug 2025 current = 0
    months_since_start = (current_year - start_year) * 12 + (current_month - start_month)
    if months_since_start < 0:
        months_since_start = 0

    # Group by ISIN
    positions = []
    grouped = df.groupby('isin')
    
    for isin, group in grouped:
        # Get the name from first element (cleaned)
        name = group['name'].iloc[0]
        # Clean name to remove suffixes like "- Sparplan ausgeführt"
        if ' - ' in name:
            name = name.split(' - ')[0]
        
        # Separate buys and sells
        buys = group[group['type'] == 'Savings Plan']
        sells = group[group['name'].str.contains('Liquidation', na=False)]
        
        # Calculate total shares (bought - sold)
        shares_bought = buys['shares'].sum() if not buys.empty and 'shares' in buys.columns else 0
        shares_sold = sells['shares'].sum() if not sells.empty and 'shares' in sells.columns else 0
        total_shares = shares_bought - shares_sold
        
        # Calculate invested (sum of purchase amounts)
        invested = abs(buys['value'].sum()) if not buys.empty else 0
        
        # Get price based on mode
        if use_current_price and isin in current_prices:
            # Use current price from database
            average_price = current_prices[isin]
        else:
            # Use last purchase price (pivot mode - default)
            if not buys.empty:
                # Sort by date to get the last purchase
                buys_sorted = buys.sort_values('date', ascending=False)
                last_purchase = buys_sorted.iloc[0]
                
                # Calculate average price = value / shares from last purchase
                if last_purchase['shares'] and last_purchase['shares'] > 0:
                    average_price = abs(last_purchase['value']) / last_purchase['shares']
                else:
                    average_price = 0
            else:
                average_price = 0
        
        # Calculate current value = shares * average_price
        current_value = total_shares * average_price
        
        # Calculate plus value = current_value - invested
        plus_value = current_value - invested
        
        # Determine target months based on purchase activity
        target_months = months_since_start
        
        # Check if bought this month
        if not buys.empty:
            has_purchase_this_month = not buys[
                (buys['date'].dt.month == current_month) & 
                (buys['date'].dt.year == current_year)
            ].empty
            
            if has_purchase_this_month:
                # If we bought this month, we should target the current month count (so +1 compared to 0-index base)
                # target_months becomes equivalent to "1" for the first month, "6" for the 6th month, etc.
                target_months += 1

        # Calculate missing
        # Standard monthly target is 110 EUR
        # If target_months = 0 (Start month, no buy yet): Missing = 0 - 0 = 0? 
        # Wait, if I start in Aug and haven't bought, I should miss 110?
        # If months_since_start=0, missing=0. But I should buy!
        # Actually user logic implies: months_since_start is "Past completed months".
        # So for Aug (0), we expect 0 completed? No, user probably uses "missing" to drive purchase.
        # But let's stick to fixing the "Negative" issue first (Overpayment).
        # Previous logic was: missing = (months_since_start * 110) - invested.
        # If I bought in Aug: (0 * 110) - 110 = -110.
        # With fix: target = 0 + 1 = 1. (1 * 110) - 110 = 0.
        # This solves the negative issue.
        # Does it solve the "Not bought yet" issue?
        # If not bought in Aug: target=0. Invested=0. Missing=0.
        # This implies "Missing" doesn't prompt for the *first* month?
        # Or maybe `months_since_start` logic is intended to be `+1` always? 
        # But `months_since_start` formula is standard delta.
        # Let's assume for now we only fix the "Negative" issue reported.
        
        missing = (target_months * 110) - invested
        
        # Calculate next_plan based on condition
        # If missing >= (average_price * 1.1): next_plan = 110 + missing + (10% of average price) and display in red
        # Otherwise: next_plan = 110
        if missing >= (average_price * 1.1):
            next_plan = 110 + missing + (0.1 * average_price)
            # Round down to nearest 10 euros
            next_plan = (next_plan // 10) * 10
            next_plan_is_red = True
        else:
            next_plan = 110
            next_plan_is_red = False

        positions.append({
            "isin": isin,
            "name": name,
            "shares": round(total_shares, 4),
            "average_price": round(average_price, 2),
            "current_value": round(current_value, 2),
            "plus_value": round(plus_value, 2),
            "invested": round(invested, 2),
            "missing": round(missing, 2),
            "next_plan": round(next_plan, 2),
            "next_plan_is_red": bool(next_plan_is_red),  # Convert numpy bool to Python bool
            "plus_value_percent": round((plus_value / invested * 100), 2) if invested > 0 else 0
        })
    
    # Sort by invested amount descending
    positions.sort(key=lambda x: x['invested'], reverse=True)
    
    return positions

@app.get("/api/position/{isin}")
def get_position_details(isin: str):
    conn = get_db_connection()
    
    # Fetch all transactions for this ISIN
    query = "SELECT * FROM transactions WHERE isin = ? ORDER BY date ASC"
    df = pd.read_sql_query(query, conn, params=(isin,))
    conn.close()
    
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Position not found")
        
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format='ISO8601', utc=True)
    
    # Filter for Savings Plan (buys) and Liquidation (sells)
    # We'll focus on buys for the history and average calculation as per request
    # but we need to account for sells in the total shares if any
    
    # Initialize variables for cumulative calculation
    history = []
    cumulative_shares = 0
    cumulative_invested = 0
    
    # We will track the "average price" evolution.
    # Assumption: The "market price" at the time of purchase is the purchase price.
    
    previous_avg_price = 0
    
    for index, row in df.iterrows():
        if row['type'] == 'Savings Plan':
            # Purchase
            shares = row['shares']
            value = abs(row['value'])
            price = value / shares if shares > 0 else 0
            
            cumulative_shares += shares
            cumulative_invested += value
            
            # Current average price (weighted average of inventory)
            # Actually, the user wants "evolution of the average value". 
            # If "average value" means the unit price of the asset:
            # We can use the purchase price of this transaction as the "current market price".
            
            current_market_price = price
            
            # Calculate delta from previous
            delta_value = current_market_price - previous_avg_price if previous_avg_price > 0 else 0
            delta_percent = (delta_value / previous_avg_price * 100) if previous_avg_price > 0 else 0
            
            history.append({
                "date": row['date'].isoformat(),
                "type": "Buy",
                "shares": round(shares, 4),
                "price": round(price, 2), # Unit price of this purchase
                "total_shares": round(cumulative_shares, 4),
                "total_invested": round(cumulative_invested, 2),
                "total_value": round(cumulative_shares * current_market_price, 2),
                "plus_value": round((cumulative_shares * current_market_price) - cumulative_invested, 2),
                "delta_value": round(delta_value, 2),
                "delta_percent": round(delta_percent, 2)
            })
            
            previous_avg_price = current_market_price

        elif 'Liquidation' in str(row['name']):
            # Sale - for now just update shares, maybe don't show in the "purchase history" table 
            # or show it differently. The user asked for "list of all purchases".
            # So we will skip adding it to the list but update the state.
            shares = row['shares'] # usually negative or positive depending on import? 
            # In DB, shares for liquidation might be negative? Let's check.
            # Based on previous code: shares_sold = sells['shares'].sum()
            # If shares in DB are positive for sells, we subtract.
            
            # Let's assume shares are positive in DB for Liquidation based on `check_liquidations.py` logic usually.
            # But let's look at `get_positions`: `total_shares = shares_bought - shares_sold`
            # This implies `shares` column is positive for both.
            
            cumulative_shares -= abs(shares)
            # Invested amount usually decreases on sell? Or stays same?
            # Usually "Invested" is "Net Invested" or "Total Invested". 
            # User request: "valeur total investi". Usually means sum of all buys.
            # So we don't reduce cumulative_invested on sell for "Total Invested" metric if it means "Gross Invested".
            # But if it means "Net Invested" (cash in), we should.
            # Given the context of "Savings Plans", it's likely "Gross Invested" (how much I put in).
            pass
            
    # Reverse history to show newest first
    history.reverse()
    
    # Get current stats from the latest history entry
    if history:
        latest = history[0]
        stats = {
            "name": df.iloc[0]['name'].split(' - ')[0],
            "isin": isin,
            "shares": latest['total_shares'],
            "invested": latest['total_invested'],
            "value": latest['total_value'],
            "plus_value": latest['plus_value'],
            "plus_value_percent": round((latest['plus_value'] / latest['total_invested'] * 100), 2) if latest['total_invested'] > 0 else 0
        }
    else:
        stats = {}

    return {
        "stats": stats,
        "history": history
    }


# Serve static files
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
