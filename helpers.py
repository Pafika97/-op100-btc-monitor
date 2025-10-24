
# helpers.py
import requests, time, logging, sqlite3, os
from bs4 import BeautifulSoup
from decimal import Decimal

USER_AGENT = "btc-top100-monitor/1.0 (+https://example)"

def fetch_top100_bitinfocharts(limit=100):
    \"\"\"Scrape bitinfocharts top-100 richest bitcoin addresses page.
    Returns list of dicts: {rank:int, address:str, balance_sats:int, balance_btc:Decimal}
    \"\"\"
    url = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses.html"
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # The table rows are in <table class="table..."> - attempt to find the first table
    table = soup.find("table")
    if not table:
        raise RuntimeError("Top-100 table not found on bitinfocharts page")
    rows = table.find_all("tr")
    result = []
    for tr in rows[1:limit+1]:  # skip header
        cols = tr.find_all(["td","th"])
        if len(cols) < 3:
            continue
        rank = int(cols[0].get_text(strip=True).replace(".", "").replace("#",""))
        addr = cols[1].get_text(strip=True)
        balance_text = cols[2].get_text(strip=True).replace(",", "").split()[0]  # BTC value
        try:
            balance_btc = Decimal(balance_text)
        except:
            balance_btc = Decimal("0")
        balance_sats = int(balance_btc * Decimal(1e8))
        result.append({"rank": rank, "address": addr, "balance_btc": balance_btc, "balance_sats": balance_sats})
        if len(result) >= limit:
            break
    return result

def fetch_top100_blockchair(limit=100, api_key=None):
    \"\"\"Fetch top addresses using Blockchair API (best-effort). If it fails, raises exception.
    Note: Blockchair may require specific query permissions or API key for high rate.
    \"\"\"
    base = "https://api.blockchair.com/bitcoin/addresses"
    params = {"limit": limit, "offset": 0, "fields": "address,spent_output_total,received,balance", "sort": "balance(desc)"}
    headers = {"User-Agent": USER_AGENT}
    if api_key:
        headers["x-api-key"] = api_key
    resp = requests.get(base, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # Blockchair returns data in data[]. Extract addresses and balances
    result = []
    items = data.get("data") or []
    rank = 1
    for k,v in items.items() if isinstance(items, dict) else items:
        # accommodate both dict and list forms
        if isinstance(items, dict):
            row = items[k]
        else:
            row = v
        addr = row.get("address")
        balance = int(row.get("balance", 0))
        result.append({"rank": rank, "address": addr, "balance_sats": balance, "balance_btc": balance/1e8})
        rank += 1
        if rank > limit:
            break
    return result

def diff_lists(prev, curr):
    \"\"\"Compute human-readable differences between two top lists.
    prev and curr are lists of dicts with keys: address, balance_sats, rank
    Returns list of strings describing events.
    \"\"\"
    events = []
    prev_map = {p['address']: p for p in prev}
    curr_map = {c['address']: c for c in curr}
    # New addresses in curr not in prev
    for addr, obj in curr_map.items():
        if addr not in prev_map:
            events.append(f\"NEW #{obj['rank']}: {addr} ({obj['balance_sats']/1e8:.8f} BTC)\")
        else:
            p = prev_map[addr]
            # rank change
            if p.get('rank') != obj.get('rank'):
                events.append(f\"RANK {p.get('rank')} -> {obj.get('rank')}: {addr}\")
            # balance change beyond small threshold (e.g., 0.01 BTC)
            delta = obj['balance_sats'] - p['balance_sats']
            if abs(delta) >= 1000000:  # >=0.01 BTC
                events.append(f\"BALANCE change for {addr}: {p['balance_sats']/1e8:.8f} -> {obj['balance_sats']/1e8:.8f} BTC ({delta/1e8:+.8f})\")
    # Removed addresses (present in prev but not in curr)
    for addr, p in prev_map.items():
        if addr not in curr_map:
            events.append(f\"REMOVED #{p.get('rank')}: {addr} ({p['balance_sats']/1e8:.8f} BTC)\")
    return events

def ensure_db(path):
    need_init = not os.path.exists(path)
    conn = sqlite3.connect(path, check_same_thread=False)
    if need_init:
        c = conn.cursor()
        c.execute(\"\"\"CREATE TABLE holders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank INTEGER,
            addr TEXT,
            balance_sats INTEGER
        )\"\"\")
        conn.commit()
    return conn

def send_telegram_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()
