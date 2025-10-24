
# main.py
# Bitcoin Top-100 Holders Monitor -> sends updates to a Telegram chat when the top-100 list changes.
# Usage: copy config.example.yaml to config.yaml, fill values, then: python main.py

import time, logging, sqlite3, yaml, sys
from helpers import fetch_top100_bitinfocharts, fetch_top100_blockchair, diff_lists, send_telegram_message, ensure_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def load_config(path="config.yaml"):
    import os
    if not os.path.exists(path):
        logging.error("Config file %s not found. Copy config.example.yaml -> config.yaml and edit.", path)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()
    poll_interval = int(cfg.get("poll_interval_seconds", 300))
    source = cfg.get("source", "bitinfocharts")  # or "blockchair"
    blockchair_api_key = cfg.get("blockchair_api_key")

    conn = ensure_db(os.path.join(".", "monitor.db"))
    last = None

    logging.info("Starting monitor: source=%s poll_interval=%ss", source, poll_interval)

    while True:
        try:
            if source == "blockchair":
                top100 = fetch_top100_blockchair(limit=100, api_key=blockchair_api_key)
            else:
                top100 = fetch_top100_bitinfocharts(limit=100)

            # store and diff
            c = conn.cursor()
            # Load previous list
            c.execute("SELECT addr, balance_sats, rank FROM holders ORDER BY rank ASC")
            rows = c.fetchall()
            prev = [{"address": r[0], "balance_sats": r[1], "rank": r[2]} for r in rows]

            changes = diff_lists(prev, top100)

            if changes:
                msg = f"Top-100 BTC holders changes ({len(changes)} events):\\n"
                for ev in changes:
                    msg += f"- {ev}\\n"
                logging.info("Detected changes, sending Telegram message")
                send_telegram_message(cfg["telegram_bot_token"], cfg["telegram_chat_id"], msg)

                # Replace stored table with new snapshot
                c.execute("DELETE FROM holders")
                for item in top100:
                    c.execute("INSERT INTO holders (rank, addr, balance_sats) VALUES (?, ?, ?)",
                              (item['rank'], item['address'], item['balance_sats']))
                conn.commit()
            else:
                logging.debug("No changes detected")

        except Exception as e:
            logging.exception("Error during polling loop: %s", e)
            try:
                send_telegram_message(cfg["telegram_bot_token"], cfg["telegram_chat_id"],
                                      f"Monitor error: {e}")
            except Exception:
                logging.exception("Failed to send error to Telegram")

        time.sleep(poll_interval)

if __name__ == '__main__':
    main()
