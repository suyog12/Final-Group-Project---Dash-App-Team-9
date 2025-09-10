import os
import time
import pandas as pd
import requests

API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "").strip()
if not API_KEY:
    raise SystemExit("Set ALPHAVANTAGE_API_KEY in your environment before running.")

BASE = "https://www.alphavantage.co/query"
TICKERS = ["AAPL", "MSFT"]
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_csv(url, expect_cols, max_tries=6, sleep_sec=15):
    """Request CSV; retry if throttled or schema is wrong."""
    for i in range(1, max_tries + 1):
        r = requests.get(url, timeout=30)
        text = r.text.strip()

        # Alpha Vantage throttling returns JSON with a "Note" or "Information"
        if text.startswith("{") or "Note" in text or "Information" in text:
            print(f"[try {i}] throttled; waiting {sleep_sec}s")
            time.sleep(sleep_sec)
            continue

        df = pd.read_csv(pd.compat.StringIO(text)) if hasattr(pd.compat, "StringIO") else pd.read_csv(pd.io.common.StringIO(text))

        # Some responses return 'timestamp' instead of 'date' – normalize here
        if "timestamp" in df.columns and "date" not in df.columns:
            df = df.rename(columns={"timestamp": "date"})

        if all(col in df.columns for col in expect_cols):
            return df

        print(f"[try {i}] unexpected columns {list(df.columns)}; waiting {sleep_sec}s")
        time.sleep(sleep_sec)

    raise RuntimeError("Could not fetch a valid CSV after retries.")

def fetch_daily(symbol: str):
    url = (
        f"{BASE}?function=TIME_SERIES_DAILY&symbol={symbol}"
        f"&outputsize=full&datatype=csv&apikey={API_KEY}"
    )
    df = fetch_csv(url, expect_cols=["date", "close"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["symbol"] = symbol
    df = df.dropna(subset=["date", "close"]).sort_values("date")
    out = os.path.join(CACHE_DIR, f"{symbol}_daily.csv")
    df[["date", "close", "symbol"]].to_csv(out, index=False)
    print("wrote", out)

def fetch_daily_ohlc(symbol: str):
    url = (
        f"{BASE}?function=TIME_SERIES_DAILY&symbol={symbol}"
        f"&outputsize=full&datatype=csv&apikey={API_KEY}"
    )
    df = fetch_csv(url, expect_cols=["date", "open", "high", "low", "close"])
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["symbol"] = symbol
    df = df.dropna(subset=["date", "open", "high", "low", "close"]).sort_values("date")
    out = os.path.join(CACHE_DIR, f"{symbol}_daily_ohlc.csv")
    df[["date", "open", "high", "low", "close", "symbol"]].to_csv(out, index=False)
    print("wrote", out)

if __name__ == "__main__":
    for t in TICKERS:
        fetch_daily(t)
        fetch_daily_ohlc(t)
    print("Cache ready:", os.listdir(CACHE_DIR))
