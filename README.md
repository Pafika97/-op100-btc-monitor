
# Bitcoin Top-100 Holders Monitor

This project monitors the Bitcoin "top 100 richest addresses" list (from bitinfocharts or Blockchair)
and sends updates to a Telegram chat when the list changes (new addresses enter, addresses leave,
rank changes, or balance changes beyond a small threshold).

## Files
- `main.py` — Main monitor loop.
- `helpers.py` — Fetchers, diffing logic, DB, Telegram sender.
- `config.example.yaml` — Example config. Copy to `config.yaml` and edit.
- `requirements.txt` — Python dependencies.

## Quick start
1. Install Python 3.10+.
2. Create a virtualenv and install deps:
   ```
   python -m venv venv
   source venv/bin/activate    # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt
   ```
3. Copy `config.example.yaml` -> `config.yaml` and fill:
   - `telegram_bot_token` — token from @BotFather
   - `telegram_chat_id` — your chat id (use @userinfobot or similar to get it; for groups make sure the bot is added)
   - `poll_interval_seconds` — polling interval
   - `source` — choose `bitinfocharts` (scraping) or `blockchair` (API)
   - If you use `blockchair`, optionally add `blockchair_api_key`.
4. Run:
   ```
   python main.py
   ```

## Notes and caveats
- **Addresses vs entities**: Bitcoin uses the UTXO model; a single entity (exchange, custodial service, user) may control many addresses. "Top addresses" are raw addresses and are not reconciled to real-world owners. Some top addresses belong to exchanges (Binance, Coinbase cold wallets), custodial services, or are multisig.
- **Data sources**:
  - `bitinfocharts` — public web page with top-100 table (scraped by this script). Fast and simple but scraping may break if site changes.
  - `Blockchair` — official API with richer querying. May require an API key and has rate limits.
  - Other services with "rich list" functionality: Bitinfocharts, CoinCarp, OKLink, Tokenview, CoinLore.
- **Reliability**: For production usage, prefer a reliable API (Blockchair, paid providers) rather than scraping.
- **Improvements**:
  - Add address clustering heuristics (Tag clusters to group exchange wallets).
  - Add historical snapshots and change visualization.
  - Add alerts for thresholds (e.g., an address moving > X BTC).
  - Persist enhanced metadata (tag names, known exchange labels) using third-party label datasets (e.g., walletexplorer, blockchair labels).

## License
MIT-style; feel free to adapt.
