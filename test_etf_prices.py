"""
Test script to verify the ETF prices system is working correctly.
"""
import sqlite3
from datetime import datetime

DB_PATH = "data/trade_republic.db"

def test_table_exists():
    """Test if the etf_prices table exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='etf_prices'
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print("OK - Table 'etf_prices' exists")
        return True
    else:
        print("ERROR - Table 'etf_prices' does not exist")
        return False

def test_table_structure():
    """Test if the table has the correct structure."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(etf_prices)")
    columns = cursor.fetchall()
    conn.close()
    
    expected_columns = ['id', 'isin', 'date', 'price', 'created_at']
    actual_columns = [col[1] for col in columns]
    
    if all(col in actual_columns for col in expected_columns):
        print(f"OK - Table structure is correct: {actual_columns}")
        return True
    else:
        print(f"ERROR - Table structure is incorrect. Expected: {expected_columns}, Got: {actual_columns}")
        return False

def test_unique_constraint():
    """Test if the unique constraint on (isin, date) works."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    test_isin = "TEST123456789"
    test_date = datetime.now().strftime('%Y-%m-%d')
    test_price = 100.50
    
    try:
        # Insert first record
        cursor.execute("""
            INSERT INTO etf_prices (isin, date, price)
            VALUES (?, ?, ?)
        """, (test_isin, test_date, test_price))
        conn.commit()
        
        # Try to insert duplicate
        cursor.execute("""
            INSERT INTO etf_prices (isin, date, price)
            VALUES (?, ?, ?)
        """, (test_isin, test_date, test_price + 10))
        conn.commit()
        
        print("ERROR - Unique constraint is not working (duplicate was inserted)")
        success = False
        
    except sqlite3.IntegrityError:
        print("OK - Unique constraint is working (duplicate was rejected)")
        success = True
    
    finally:
        # Clean up test data
        cursor.execute("DELETE FROM etf_prices WHERE isin = ?", (test_isin,))
        conn.commit()
        conn.close()
    
    return success

def test_data_count():
    """Show how many price records are in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM etf_prices")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT isin) FROM etf_prices")
    unique_isins = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"INFO - Database contains {count} price records for {unique_isins} unique ISINs")
    return True

def test_recent_prices():
    """Show the most recent prices."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT isin, date, price 
        FROM etf_prices 
        ORDER BY date DESC, isin 
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        print("\nINFO - Most recent prices:")
        for isin, date, price in results:
            print(f"  {isin}: {price}€ on {date}")
    else:
        print("\nINFO - No prices in database yet. Run 'python src/fetch_etf_prices.py' to fetch prices.")
    
    return True

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("ETF Prices System - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Table Existence", test_table_exists),
        ("Table Structure", test_table_structure),
        ("Unique Constraint", test_unique_constraint),
        ("Data Count", test_data_count),
        ("Recent Prices", test_recent_prices),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTest: {name}")
        print("-" * 60)
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"ERROR - Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status:6} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! The ETF prices system is ready to use.")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    run_all_tests()
