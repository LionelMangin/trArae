# Trade Republic Portfolio Dashboard

A standalone Python application to retrieve your Trade Republic transaction history, store it in a local SQLite database, and visualize it with a premium web dashboard.

## Features
-   **Automatic Data Retrieval**: Fetches transaction history directly from Trade Republic using `pytr`.
-   **Smart Synchronization**: Detects new transactions and updates your local database without duplication.
-   **Local Privacy**: Your financial data is stored locally in an SQLite database (`data/trade_republic.db`).
-   **Premium Dashboard**: A beautiful, dark-mode web interface to visualize your portfolio performance, asset allocation, and transaction history.

## Prerequisites
-   **OS**: Windows, macOS, or Linux.
-   **Python**: Version 3.9 or higher.
-   **Trade Republic Account**: You need an active account to fetch data.

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd tradeRepubliqueAraeStandalone
```

### 2. Set up a virtual environment
It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration

1.  **Create the configuration file**:
    Copy the example config file to `config/config.ini`.
    ```bash
    # Windows
    copy config\config.ini.example config\config.ini
    
    # macOS/Linux
    cp config/config.ini.example config/config.ini
    ```

2.  **Edit credentials**:
    Open `config/config.ini` and enter your Trade Republic phone number and PIN.
    ```ini
    [pytr]
    phone_number = +33612345678
    pin = 1234
    ```

## Usage

### 1. Synchronize Data
Run the synchronization script to fetch the latest data from Trade Republic.

```bash
python -m src.main
```
*Note: On the first run, you will be asked to enter the 2FA code sent to your mobile app to authorize the device.*

### 2. Launch the Dashboard
Start the web server to view your portfolio.

```bash
python -m uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the App
Open your web browser and go to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

## Project Structure
For developers or AI agents working on this project, please refer to [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a detailed technical overview.

-   `src/`: Application source code.
-   `data/`: Database storage.
-   `config/`: Configuration files.
