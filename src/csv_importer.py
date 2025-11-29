import csv
from typing import List
from datetime import datetime
from .models import Transaction

class CsvImporter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[Transaction]:
        transactions = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            # Detect delimiter (the example file seemed to use ';')
            # We'll read the first line to check
            first_line = f.readline()
            delimiter = ';' if ';' in first_line else ','
            f.seek(0)
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                # Example row: Date;Type;Value;Note;ISIN;Shares;Fees;Taxes
                # 2025-08-12T09:38:26;Deposit;700.0;MELLE CARLA CHAVATTE;;;;
                
                try:
                    # Parse value (handle potential comma vs dot decimals if needed, though example showed dots)
                    value = float(row['Value'])
                    shares = float(row['Shares']) if row.get('Shares') else None
                    fees = float(row['Fees']) if row.get('Fees') else 0.0
                    taxes = float(row['Taxes']) if row.get('Taxes') else 0.0
                    
                    # Parse date (remove 'T' if present for consistency, or keep as is)
                    # The DB schema expects TEXT, so ISO format is fine.
                    date_str = row['Date']
                    
                    t = Transaction(
                        date=date_str,
                        type=row['Type'],
                        value=value,
                        isin=row.get('ISIN') or None, # Handle empty strings as None
                        name=row.get('Note'), # Using Note as Name/Description
                        shares=shares,
                        fees=fees,
                        taxes=taxes
                    )
                    transactions.append(t)
                except ValueError as e:
                    print(f"Skipping row due to error: {e} | Row: {row}")
                    continue
                    
        return transactions
