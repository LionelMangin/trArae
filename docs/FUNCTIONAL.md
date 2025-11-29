# Functional Documentation

## 1. Project Overview
The **Trade Republic Portfolio Dashboard** is a personal finance tool designed to give users a comprehensive and private view of their Trade Republic investments. Unlike the mobile app, this dashboard runs locally on your computer, ensuring that your data remains yours. It allows for advanced analysis, better visualization on larger screens, and custom metrics that might not be available in the official app.

## 2. Core Features

### 2.1 Data Synchronization
-   **Direct Integration**: The application connects directly to Trade Republic's servers using your credentials.
-   **Secure Authentication**: Supports 2-Factor Authentication (2FA) via the Trade Republic mobile app.
-   **Incremental Updates**: The system is smart enough to only fetch new transactions since the last update, making subsequent syncs very fast.
-   **Local Storage**: All data (transactions, prices, history) is stored in a local SQLite database (`data/trade_republic.db`), giving you full access to your raw financial data.

### 2.2 Portfolio Dashboard
The dashboard serves as the main control center, providing an immediate snapshot of your financial health.
-   **Total Valuation**: Real-time calculation of your total portfolio value based on the latest available prices.
-   **Performance Metrics**:
    -   **Invested Amount**: Total cash actually invested (net of withdrawals).
    -   **Unrealized Gains/Losses**: The difference between the current value and the invested amount.
    -   **Performance %**: The percentage growth or decline of the portfolio.

### 2.3 Position Tracking
Detailed breakdown of every asset (Stock, ETF, Crypto) currently held in the portfolio.
-   **Asset Details**: Name, ISIN, and ticker symbol.
-   **Quantity**: Total number of shares held.
-   **Average Buy Price (PRU)**: Calculated average price per share based on all historical purchases.
-   **Current Value**: Quantity × Current Market Price.
-   **Plus/Minus Value**: The absolute and percentage gain/loss for each specific asset.
-   **"Next Plan" Indicator**: A custom metric helping users decide on their next investment move based on portfolio balance.

### 2.4 Transaction History
A complete, searchable ledger of every movement in the account.
-   **Types**: Distinguishes between Deposits, Withdrawals, Buy Orders (Savings Plans & One-offs), Sells, Dividends, and Fees.
-   **Filtering**: (Planned) Ability to filter by date, asset, or transaction type.

### 2.5 Analytics & Allocation
-   **Asset Allocation**: Visual charts showing the distribution of the portfolio across different assets or asset classes.
-   **Dividend Tracking**: (Planned) Dedicated view for dividend income over time.

## 3. Business Logic & Rules

### 3.1 Transaction Classification
The system automatically categorizes raw API events into meaningful transaction types:
-   **Purchases**: Includes both manual buy orders and automated "Savings Plan" executions.
-   **Sales**: Includes manual sell orders and "Liquidations".
-   **Deposits**: Identified by specific bank transfer patterns (e.g., incoming transfers from linked bank accounts).

### 3.2 Position Calculation
-   **Net Quantity**: `Sum(Shares Bought) - Sum(Shares Sold)`.
-   **Average Price**: Calculated using the weighted average of purchase prices.
-   **Blacklisting**: Specific ISINs can be "blacklisted" via configuration to exclude them from calculations (e.g., for assets you no longer wish to track or are erroneous).

### 3.3 Privacy & Security
-   **No Cloud Sync**: Data never leaves your local machine (except for the initial fetch from Trade Republic).
-   **Credential Safety**: Credentials are stored in a local configuration file and are only used to authenticate directly with Trade Republic.

## 4. User Workflow
1.  **Sync**: User runs the sync script (`python -m src.main`) to update the database.
2.  **Analyze**: User opens the web dashboard to review performance and make decisions.
3.  **Export**: (Optional) User can access the raw SQLite database to export data to Excel/CSV for further analysis.
