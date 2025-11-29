import sqlite3
import hashlib
import json
from pathlib import Path
from .models import Transaction

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tr_id TEXT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    value REAL NOT NULL,
                    currency TEXT DEFAULT 'EUR',
                    isin TEXT,
                    name TEXT,
                    shares REAL,
                    fees REAL,
                    taxes REAL,
                    data_hash TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, type, value, isin)
                )
            ''')
            conn.commit()

    def calculate_hash(self, transaction: Transaction) -> str:
        # Create a hash based on the core fields to detect changes
        data = {
            "date": transaction.date,
            "type": transaction.type,
            "value": transaction.value,
            "isin": transaction.isin,
            "shares": transaction.shares,
            "fees": transaction.fees,
            "taxes": transaction.taxes
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def upsert_transaction(self, transaction: Transaction) -> str:
        """
        Returns:
            'inserted': New record created
            'updated': Existing record updated (hash changed)
            'skipped': Existing record identical
        """
        current_hash = self.calculate_hash(transaction)
        transaction.data_hash = current_hash

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check for existing record by composite key (Date, Type, Value, ISIN)
            # We use this composite key because tr_id might not always be available or consistent across sources (CSV vs API)
            query = '''
                SELECT id, data_hash FROM transactions 
                WHERE date = ? AND type = ? AND value = ? AND (isin = ? OR isin IS NULL)
            '''
            params = (transaction.date, transaction.type, transaction.value, transaction.isin)
            cursor.execute(query, params)
            existing = cursor.fetchone()

            if existing:
                existing_id, existing_hash = existing
                if existing_hash != current_hash:
                    # Update
                    cursor.execute('''
                        UPDATE transactions 
                        SET name=?, shares=?, fees=?, taxes=?, data_hash=?, updated_at=CURRENT_TIMESTAMP, tr_id=?
                        WHERE id=?
                    ''', (
                        transaction.name, transaction.shares, transaction.fees, transaction.taxes, 
                        current_hash, transaction.tr_id, existing_id
                    ))
                    return 'updated'
                else:
                    return 'skipped'
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO transactions (tr_id, date, type, value, currency, isin, name, shares, fees, taxes, data_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction.tr_id, transaction.date, transaction.type, transaction.value, 
                    transaction.currency, transaction.isin, transaction.name, transaction.shares, 
                    transaction.fees, transaction.taxes, current_hash
                ))
                return 'inserted'
