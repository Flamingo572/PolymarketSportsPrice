# PolyMarket Trading Bot

A Python-based trading bot for [Polymarket](https://polymarket.com/), utilizing the Polymarket CLOB (Central Limit Order Book) and Sports APIs. This bot monitors market prices and sports game states (scores, elapsed time) to identify trading signals and execute trades.

## Project Structure

- `ascincioListenRead.py`: The main asynchronous entry point. It connects to both Market and Sports WebSockets simultaneously, processes incoming data, and contains the core trade logic.
- `findIDs.py`: Utility functions to resolve market slugs into Game IDs, Token IDs, and Outcomes using the Polymarket Gamma API.
- `findSportByID.py`: Script to search for and list active sports markets.
- `marketRead.py`: Handles WebSocket connections and order book management for the Polymarket CLOB.
- `sportsRead.py`: Handles WebSocket connections for real-time sports data (scores, game state).
- `apiKeys.py`: (Ignored by git) Should contain your Polymarket API credentials and Private Key.
- `mainPrices.py`: A legacy/utility script for basic price and score reading.

## Features

- **Real-time Monitoring**: Uses WebSockets for low-latency updates from both market and sports data sources.
- **Asynchronous Execution**: Leverages `asyncio` to handle multiple data streams and trade logic concurrently.
- **Market Analysis**: Processes order book snapshots, price changes, and trade executions.
- **Sports Integration**: Tracks live scores and game status to trigger trades based on on-field events.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install requests websockets py-clob-client websocket-client
    ```

2.  **Configuration**:
    - Create an `apiKeys.py` file based on the template in the project (or ensure your existing one is correctly configured).
    - **Note**: Keep your Private Key and API credentials secure. `apiKeys.py` is included in `.gitignore` to prevent accidental commits.

3.  **Find a Market Slug**:
    Identify the market you want to trade on Polymarket (e.g., `epl-sun-ful-2026-02-22`).

## Usage

To start the bot for a specific market slug, run:

```bash
python ascincioListenRead.py
```

You can modify the `slug` variable in the `if __name__ == "__main__":` block of `ascincioListenRead.py` to target different markets.

## Trade Logic

The core trade logic is located in the `executeTradeLogic` function within `ascincioListenRead.py`. It receives updates from both `market` and `sports` sources and can be extended to include your specific mathematical models or strategy triggers.

## Security Warning

This bot requires your Polymarket Private Key to interact with the CLOB. Never share your `apiKeys.py` file or commit it to a public repository.
