from typing import List, Dict
from .models import Transaction
from .db import Database
import logging

logger = logging.getLogger(__name__)

class Importer:
    def __init__(self, db: Database, blacklist_isins: List[str] = None):
        self.db = db
        self.blacklist_isins = blacklist_isins or []

    def process_transactions(self, transactions: List[Transaction]) -> Dict[str, int]:
        stats = {
            "total": len(transactions),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "blacklisted": 0
        }

        for transaction in transactions:
            if transaction.isin in self.blacklist_isins:
                stats["blacklisted"] += 1
                continue

            result = self.db.upsert_transaction(transaction)
            stats[result] += 1
            
            if result == 'updated':
                logger.warning(f"Transaction updated: {transaction.date} {transaction.type} {transaction.value} {transaction.isin}")
        
        return stats
