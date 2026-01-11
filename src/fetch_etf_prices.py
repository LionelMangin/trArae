"""
Script to fetch current ETF prices from the web and store them in the database.
Only one price per day per ETF is stored (using UNIQUE constraint).
"""
import sqlite3
import requests
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/trade_republic.db"

def get_all_isins():
    """Get all unique ISINs from transactions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT isin 
        FROM transactions 
        WHERE isin IS NOT NULL 
        AND (type = 'Savings Plan' OR name LIKE '%Liquidation%')
    """)
    
    isins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return isins

def load_isin_mapping():
    """Load ISIN to ticker mapping from database."""
    mapping = {}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='etf_mapping'")
        if not cursor.fetchone():
            logger.warning("Table etf_mapping does not exist")
            return mapping

        cursor.execute("SELECT isin, ticker FROM etf_mapping")
        rows = cursor.fetchall()
        
        for row in rows:
            isin, ticker = row
            if isin and ticker:
                mapping[isin] = ticker
                
        logger.info(f"Loaded {len(mapping)} ISIN mappings from database")
        conn.close()
    except Exception as e:
        logger.error(f"Error loading mapping from database: {e}")
    
    return mapping

# Load mapping once at module level
ISIN_MAPPING = load_isin_mapping()

def save_mapping_to_db(isin, ticker):
    """Save a discovered mapping to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO etf_mapping (isin, ticker, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (isin, ticker))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved mapping to DB: {isin} -> {ticker}")
        
        # Update local cache
        ISIN_MAPPING[isin] = ticker
        
    except Exception as e:
        logger.error(f"Error saving mapping to DB: {e}")

def fetch_etf_price(isin):
    """
    Fetch current price for an ETF from Yahoo Finance.
    
    Args:
        isin: The ISIN code of the ETF
        
    Returns:
        float: Current price or None if not found
    """
    # Try to get ticker from mapping first
    if isin in ISIN_MAPPING:
        ticker = ISIN_MAPPING[isin]
        logger.info(f"Using mapped ticker for {isin}: {ticker}")
        
        # Try fetching with mapped ticker
        price = fetch_price_from_yahoo(ticker)
        if price:
            return price
        else:
            logger.warning(f"Mapped ticker {ticker} failed for {isin}, trying alternatives...")
    
    # List of candidate tickers to try
    candidates = []
    
    # 1. Try standard suffixes based on ISIN prefix
    if isin.startswith('FR'):
        candidates.append(f"{isin}.PA")
    elif isin.startswith('IE'):
        candidates.append(f"{isin}.L")
        candidates.append(f"{isin}.DE") # Often used for EUR
        candidates.append(f"{isin}.AS")
    elif isin.startswith('LU'):
        candidates.append(f"{isin}.PA")
        candidates.append(f"{isin}.DE")
    elif isin.startswith('DE'):
        candidates.append(f"{isin}.DE")
    
    # 2. Add generic fallbacks
    candidates.append(f"{isin}.SW")
    candidates.append(f"{isin}.MI")
    
    # 3. Try to search Yahoo Finance for the ISIN
    try:
        search_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={isin}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(search_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'quotes' in data and data['quotes']:
                for quote in data['quotes']:
                    symbol = quote['symbol']
                    if symbol not in candidates:
                        candidates.insert(0, symbol) # Try searched symbol first
    except Exception as e:
        logger.warning(f"Search failed for {isin}: {e}")

    # Try all candidates
    for ticker in candidates:
        logger.info(f"Trying candidate ticker: {ticker}")
        price = fetch_price_from_yahoo(ticker)
        if price:
            logger.info(f"Found working ticker for {isin}: {ticker}")
            save_mapping_to_db(isin, ticker)
            return price
            
    logger.warning(f"Could not find working ticker for {isin}")
    return None

def fetch_price_from_yahoo(ticker):
    """Helper to fetch price for a specific ticker."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    return result['meta']['regularMarketPrice']
        return None
    except Exception:
        return None

def store_etf_price(isin, price, date=None):
    """
    Store ETF price in database. If a price already exists for this date,
    it will be replaced with the new value.
    
    Args:
        isin: The ISIN code
        price: The current price
        date: The date (defaults to today)
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if price already exists
        cursor.execute("""
            SELECT price FROM etf_prices 
            WHERE isin = ? AND date = ?
        """, (isin, date))
        
        existing = cursor.fetchone()
        
        # Insert or replace the price
        cursor.execute("""
            INSERT OR REPLACE INTO etf_prices (isin, date, price)
            VALUES (?, ?, ?)
        """, (isin, date, price))
        
        conn.commit()
        
        if existing:
            old_price = existing[0]
            logger.info(f"UPDATE - Updated price for {isin} on {date}: {old_price} -> {price}")
        else:
            logger.info(f"OK - Stored new price for {isin} on {date}: {price}")
            
    except Exception as e:
        logger.error(f"Error storing price for {isin}: {e}")
    finally:
        conn.close()

def get_latest_price(isin):
    """Get the most recent price for an ISIN from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT price, date 
        FROM etf_prices 
        WHERE isin = ? 
        ORDER BY date DESC 
        LIMIT 1
    """, (isin,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result if result else (None, None)

def update_all_prices():
    """Fetch and store current prices for all ETFs."""
    logger.info("Starting ETF price update...")
    
    isins = get_all_isins()
    logger.info(f"Found {len(isins)} unique ISINs to update")
    
    success_count = 0
    fail_count = 0
    
    for isin in isins:
        # Always fetch new price (will update if exists)
        price = fetch_etf_price(isin)
        
        if price:
            store_etf_price(isin, price)
            success_count += 1
        else:
            fail_count += 1
        
        # Be nice to the API - add a small delay
        time.sleep(1)
    
    logger.info(f"\n=== Update Complete ===")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info(f"Total: {len(isins)}")

if __name__ == "__main__":
    update_all_prices()
