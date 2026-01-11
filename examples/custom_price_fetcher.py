"""
Example: Custom ETF price fetcher using different data sources.

This file shows how to customize the price fetching logic for your specific ETFs.
You can modify fetch_etf_prices.py based on these examples.
"""

import requests
from datetime import datetime

# Example 1: Using Alpha Vantage API
def fetch_price_alpha_vantage(isin, api_key):
    """
    Fetch price using Alpha Vantage API.
    
    Note: You need to convert ISIN to ticker symbol first.
    Alpha Vantage requires an API key (free tier available).
    """
    # Convert ISIN to ticker (you need to maintain a mapping)
    ticker = isin_to_ticker(isin)
    
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': ticker,
        'apikey': api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'Global Quote' in data and '05. price' in data['Global Quote']:
        return float(data['Global Quote']['05. price'])
    
    return None

# Example 2: Using a CSV mapping file
def fetch_price_with_mapping(isin, mapping_file='config/isin_to_ticker.csv'):
    """
    Use a CSV file to map ISIN to Yahoo Finance ticker.
    
    CSV format:
    ISIN,Ticker,Exchange
    IE00B4L5Y983,IWDA.AS,Amsterdam
    LU1681043599,EUNL.DE,XETRA
    """
    import pandas as pd
    
    # Load mapping
    mapping = pd.read_csv(mapping_file)
    row = mapping[mapping['ISIN'] == isin]
    
    if row.empty:
        print(f"No mapping found for {isin}")
        return None
    
    ticker = row.iloc[0]['Ticker']
    
    # Fetch from Yahoo Finance
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                return result['meta']['regularMarketPrice']
    
    return None

# Example 3: Using multiple sources with fallback
def fetch_price_multi_source(isin):
    """
    Try multiple sources in order until one succeeds.
    """
    sources = [
        ('Yahoo Finance', lambda: fetch_price_yahoo(isin)),
        ('Alpha Vantage', lambda: fetch_price_alpha_vantage(isin, 'YOUR_API_KEY')),
        ('Manual Mapping', lambda: fetch_price_with_mapping(isin)),
    ]
    
    for source_name, fetch_func in sources:
        try:
            price = fetch_func()
            if price:
                print(f"Successfully fetched {isin} from {source_name}: {price}")
                return price
        except Exception as e:
            print(f"Failed to fetch from {source_name}: {e}")
            continue
    
    print(f"All sources failed for {isin}")
    return None

# Example 4: Using Trade Republic API (if available)
def fetch_price_trade_republic(isin):
    """
    If Trade Republic provides an API to get current prices.
    This is just a placeholder - you'd need to implement based on their API.
    """
    # This would require authentication and proper API access
    # Just an example structure
    pass

# Helper function: ISIN to ticker conversion
def isin_to_ticker(isin):
    """
    Convert ISIN to ticker symbol.
    
    This is highly specific to your ETFs. You may need to:
    1. Maintain a manual mapping file
    2. Use a third-party service
    3. Build your own database
    
    Common patterns:
    - European ETFs often trade on multiple exchanges
    - ISIN IE00B4L5Y983 might be IWDA.AS (Amsterdam) or IWDA.L (London)
    """
    
    # Example manual mapping for common ETFs
    isin_ticker_map = {
        'IE00B4L5Y983': 'IWDA.AS',  # iShares Core MSCI World
        'LU1681043599': 'EUNL.DE',  # Amundi MSCI World
        'IE00B3RBWM25': 'VWRL.AS',  # Vanguard FTSE All-World
        'IE00BK5BQT80': 'VWCE.DE',  # Vanguard FTSE All-World
        'LU0274208692': 'WTAI.DE',  # Xtrackers MSCI World
        # Add your ETFs here
    }
    
    return isin_ticker_map.get(isin, f"{isin}.SW")  # Default to Swiss exchange

# Example 5: Caching with expiration
def fetch_price_with_cache(isin, cache_hours=1):
    """
    Fetch price with in-memory cache that expires after X hours.
    Useful if you're calling this function multiple times.
    """
    import sqlite3
    from datetime import datetime, timedelta
    
    DB_PATH = "data/trade_republic.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check cache
    expiry_time = datetime.now() - timedelta(hours=cache_hours)
    cursor.execute("""
        SELECT price, created_at 
        FROM etf_prices 
        WHERE isin = ? 
        AND created_at > ?
        ORDER BY created_at DESC 
        LIMIT 1
    """, (isin, expiry_time.isoformat()))
    
    result = cursor.fetchone()
    
    if result:
        print(f"Using cached price for {isin}: {result[0]}")
        conn.close()
        return result[0]
    
    # Cache miss - fetch new price
    price = fetch_price_yahoo(isin)
    
    if price:
        # Store in cache
        cursor.execute("""
            INSERT INTO etf_prices (isin, date, price)
            VALUES (?, ?, ?)
        """, (isin, datetime.now().strftime('%Y-%m-%d'), price))
        conn.commit()
    
    conn.close()
    return price

def fetch_price_yahoo(isin):
    """Basic Yahoo Finance fetcher."""
    ticker = isin_to_ticker(isin)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                return result['meta']['regularMarketPrice']
    
    return None

# Example usage
if __name__ == "__main__":
    # Test with a sample ISIN
    test_isin = "IE00B4L5Y983"  # iShares Core MSCI World
    
    print(f"Testing price fetch for {test_isin}")
    print("-" * 60)
    
    # Try different methods
    print("\n1. Yahoo Finance:")
    price = fetch_price_yahoo(test_isin)
    print(f"   Price: {price}")
    
    print("\n2. Multi-source with fallback:")
    price = fetch_price_multi_source(test_isin)
    print(f"   Price: {price}")
    
    print("\n3. With caching:")
    price = fetch_price_with_cache(test_isin)
    print(f"   Price: {price}")
