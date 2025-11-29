import argparse
import configparser
import logging
import sys
from pathlib import Path
from .db import Database
from .importer import Importer
from .csv_importer import CsvImporter
# from .tr_api import TradeRepublicAPI # To be implemented

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Trade Republic Data Importer")
    parser.add_argument('--config', default='config/config.ini', help='Path to config file')
    parser.add_argument('--import-csv', help='Path to CSV file to import')
    args = parser.parse_args()

    # Load Config
    config = configparser.ConfigParser()
    if Path(args.config).exists():
        config.read(args.config)
    else:
        # Fallback defaults if config missing (or use example)
        pass

    db_path = config.get('database', 'path', fallback='data/trade_republic.db')
    
    # Read blacklist from config
    blacklist_str = config.get('filters', 'blacklist_isins', fallback='LU2194448267')
    blacklist_isins = [isin.strip() for isin in blacklist_str.split(',') if isin.strip()]
    
    logger.info(f"Using database: {db_path}")
    logger.info(f"Blacklisted ISINs: {blacklist_isins}")
    
    db = Database(db_path)
    importer = Importer(db, blacklist_isins=blacklist_isins)

    if args.import_csv:
        logger.info(f"Importing from CSV: {args.import_csv}")
        csv_importer = CsvImporter(args.import_csv)
        transactions = csv_importer.parse()
        stats = importer.process_transactions(transactions)
        logger.info(f"Import stats: {stats}")
    else:
        # Default to API fetch
        from .tr_api import TradeRepublicAPI
        tr_api = TradeRepublicAPI(config)
        transactions = tr_api.fetch_history()
        stats = importer.process_transactions(transactions)
        logger.info(f"Import stats: {stats}")

if __name__ == "__main__":
    main()
