from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    date: str
    type: str
    value: float
    currency: str = "EUR"
    isin: Optional[str] = None
    name: Optional[str] = None
    shares: Optional[float] = None
    fees: Optional[float] = 0.0
    taxes: Optional[float] = 0.0
    tr_id: Optional[str] = None
    data_hash: Optional[str] = None
