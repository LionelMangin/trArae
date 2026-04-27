import logging
import asyncio
from pathlib import Path
from pytr.account import login
from pytr.timeline import Timeline
from pytr.event import Event, tr_event_type_mapping, ConditionalEventType
from .models import Transaction

# Patch pytr to recognize new event types
tr_event_type_mapping["TRADING_SAVINGSPLAN_EXECUTED"] = ConditionalEventType.TRADE_INVOICE
tr_event_type_mapping["TRADING_TRADE_EXECUTED"] = ConditionalEventType.TRADE_INVOICE
tr_event_type_mapping["PEA_SAVINGS_PLAN_PAY_IN"] = ConditionalEventType.TRADE_INVOICE
tr_event_type_mapping["SAVINGS_PLAN_EXECUTED"] = ConditionalEventType.TRADE_INVOICE
tr_event_type_mapping["trading_savingsplan_executed"] = ConditionalEventType.TRADE_INVOICE
tr_event_type_mapping["trading_trade_executed"] = ConditionalEventType.TRADE_INVOICE

logger = logging.getLogger(__name__)

class TradeRepublicAPI:
    def __init__(self, config):
        self.phone_number = config.get('pytr', 'phone_number')
        self.pin = config.get('pytr', 'pin')
        self.tr = None

    def login(self):
        logger.info("Logging in to Trade Republic...")
        # Use Native App API flow to avoid WAF blocking on web endpoints
        self.tr = login(
            phone_no=self.phone_number,
            pin=self.pin,
            store_credentials=True
        )
        logger.info("Login successful.")

    def fetch_history(self):
        if not self.tr:
            self.login()
        
        logger.info("Fetching transaction history with complete details...")
        
        # Run async fetch in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self._async_fetch_history())

    async def _async_fetch_history(self):
        """
        Fetch complete transaction history using pytr's Timeline class.
        This retrieves detailed event data including shares, fees, and taxes.
        """
        # Create a temporary output path for timeline to work with
        output_path = Path("data/temp_timeline")
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create Timeline instance - this handles fetching all events with details
        timeline = Timeline(
            tr=self.tr,
            output_path=output_path,
            store_event_database=False,  # We don't need the event database file
            dump_raw_data=False  # We don't need raw JSON dumps
        )
        
        # Fetch all timeline events with their details
        logger.info("Fetching timeline events with details (this may take a moment)...")
        await timeline.tl_loop()
        
        # Convert pytr Event objects to our Transaction model
        logger.info(f"Processing {len(timeline.events)} events...")
        transactions = []
        for event_dict in timeline.events:
            # Parse event using pytr's Event class
            event = Event.from_dict(event_dict)
            
            # Convert to our Transaction model
            transaction = self._event_to_transaction(event, event_dict)
            if transaction:
                transactions.append(transaction)
        
        logger.info(f"Successfully processed {len(transactions)} transactions")
        return transactions

    def _event_to_transaction(self, event: Event, event_dict: dict) -> Transaction:
        """
        Convert a pytr Event object to our Transaction model.
        The Event class has already parsed shares, fees, taxes from the complex event structure.
        """
        try:
            # Skip events without a type (unsupported/ignored events)
            if event.event_type is None:
                return None
            
            # Get the event type string for our database
            raw_type = str(event.event_type.value) if hasattr(event.event_type, 'value') else str(event.event_type)
            
            # Map known types to readable strings
            tr_event_type = event_dict.get('eventType', '')
            subtitle = event_dict.get('subtitle', '')
            
            if raw_type == '3' or 'TRADE_INVOICE' in str(event.event_type):
                if tr_event_type in ['SAVINGS_PLAN_EXECUTED', 'trading_savingsplan_executed'] or 'Sparplan' in subtitle:
                    event_type_str = "Savings Plan"
                else:
                    event_type_str = "Trade"
            else:
                type_mapping = {
                    "2": "Savings Plan",
                    "1": "Trade"
                }
                event_type_str = type_mapping.get(raw_type, raw_type)
            
            # Build a descriptive name from title and subtitle
            title = event_dict.get('title', '')
            subtitle = event_dict.get('subtitle', '')
            name = f"{title} - {subtitle}" if subtitle else title
            
            # Get transaction ID
            tr_id = event_dict.get('id')
            
            # Format date as ISO string
            date_str = event.date.isoformat()
            
            # Currency (default to EUR)
            currency = event_dict.get('amount', {}).get('currency', 'EUR')
            
            return Transaction(
                date=date_str,
                type=event_type_str,
                value=float(event.value) if event.value is not None else 0.0,
                currency=currency,
                isin=event.isin,
                name=name,
                tr_id=tr_id,
                shares=float(event.shares) if event.shares is not None else None,
                fees=float(event.fees) if event.fees is not None else None,
                taxes=float(event.taxes) if event.taxes is not None else None
            )
        except Exception as e:
            logger.warning(f"Error converting event {event_dict.get('id')}: {e}")
            logger.debug(f"Event data: {event_dict}", exc_info=True)
            return None


