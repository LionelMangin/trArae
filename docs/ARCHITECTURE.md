# Architecture & Technical Documentation

## Overview
**Trade Republic Portfolio Dashboard** is a standalone application designed to track and visualize investment portfolios from Trade Republic. It fetches transaction history using the `pytr` library, stores it in a local SQLite database, and serves a modern web dashboard using FastAPI.

## Tech Stack
- **Language**: Python 3.9+
- **Backend Framework**: FastAPI
- **Database**: SQLite (via `sqlite3` standard library)
- **External API**: `pytr` (unofficial Trade Republic API)
- **Frontend**: Vanilla HTML/CSS/JS (no build step required)

## Project Structure

```
/
├── config/             # Configuration files
│   └── config.ini      # User credentials (phone, pin)
├── data/               # Data storage
│   └── trade_republic.db # SQLite database
├── docs/               # Documentation
├── src/                # Source Code
│   ├── static/         # Frontend Assets
│   │   ├── css/        # Stylesheets
│   │   ├── js/         # Client-side logic
│   │   └── index.html  # Main entry point
│   ├── csv_importer.py # Logic for parsing/importing CSV data
│   ├── db.py           # Database connection and queries
│   ├── main.py         # Entry point for data synchronization
│   ├── models.py       # Pydantic models for API responses
│   ├── server.py       # FastAPI application & endpoints
│   └── tr_api.py       # Integration with Trade Republic via pytr
└── requirements.txt    # Python dependencies
```

## Core Modules

### 1. Data Synchronization (`src/main.py` & `src/tr_api.py`)
- **`tr_api.py`**: Handles authentication with Trade Republic. It uses `pytr` to fetch the timeline of events.
- **`main.py`**: Orchestrates the sync process. It logs in, fetches the latest timeline events, parses them, and upserts them into the SQLite database.

### 2. Database (`src/db.py`)
- Manages the SQLite connection.
- **Key Tables**:
    - `transactions`: Stores all raw transaction data (deposits, purchases, dividends, fees).
    - `positions`: (Derived or stored) Current holding of assets.
- **Key Functions**:
    - `save_transaction()`: Inserts or updates a transaction.
    - `get_all_transactions()`: Retrieves history for the dashboard.
    - `get_positions()`: Calculates current portfolio state.

### 3. Backend API (`src/server.py`)
- Exposes REST endpoints for the frontend.
- **Endpoints**:
    - `GET /api/positions`: Returns current portfolio positions with calculated metrics (performance, allocation).
    - `GET /api/transactions`: Returns transaction history.
    - `GET /api/stats`: Returns global statistics (total invested, current value).

### 4. Frontend (`src/static/`)
- **`index.html`**: The single-page application shell.
- **`script.js`**: Fetches data from the API and renders the dashboard.
- **`styles.css`**: Custom CSS for the "premium" dark-mode aesthetic.

## Data Flow
1.  **Sync**: User runs `python -m src.main` -> Authenticates -> Fetches Events -> Saves to DB.
2.  **Serve**: User runs `server.py` -> FastAPI starts on port 8000.
3.  **View**: Browser requests `localhost:8000` -> JS fetches `/api/positions` -> Renders UI.

## Development Guidelines
- **Database Changes**: If modifying the schema in `db.py`, ensure to handle migrations or recreate the DB if backward compatibility isn't strict.
- **Frontend**: Keep it simple (Vanilla JS). Avoid introducing complex build tools (Webpack/Vite) unless necessary.
- **Code Style**: Follow PEP 8 for Python.
