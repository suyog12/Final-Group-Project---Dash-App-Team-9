import os
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")

TICKERS_DEFAULT = ["AAPL", "MSFT"]
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class DataError(Exception):
    pass

def _cache_path(symbol: str) -> str:
    return os.path.join(CACHE_DIR, f"{symbol}_daily.csv")

def _ohlc_cache_path(symbol: str) -> str:
    return os.path.join(CACHE_DIR, f"{symbol}_daily_ohlc.csv")

def _read_cache(path: str, parse_dates=None) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=parse_dates or [])
    raise DataError("Cache not found.")

def _fetch_csv(url: str) -> pd.DataFrame:
    """Fetch URL and ensure we actually got CSV (not a throttle JSON)."""
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    text = r.text.strip()

    # Alpha Vantage returns JSON error/throttle text even when datatype=csv
    looks_like_json = text.startswith("{") or '"Note"' in text or '"Information"' in text
    if looks_like_json or "Thank you for using Alpha Vantage" in text:
        raise DataError(f"Alpha Vantage throttled or returned a JSON error: {text[:240]}")

    return pd.read_csv(StringIO(text))

def fetch_daily(symbol: str, force: bool = False) -> pd.DataFrame:
    """Close-only CSV -> date, close, symbol."""
    cp = _cache_path(symbol)

    if not force and os.path.exists(cp):
        return _read_cache(cp, parse_dates=["date"])

    if not API_KEY:
        # no key: best effort – serve cache or fail clearly
        return _read_cache(cp, parse_dates=["date"])

    url = (f"{BASE}?function=TIME_SERIES_DAILY&symbol={symbol}"
           f"&outputsize=full&datatype=csv&apikey={API_KEY}")

    try:
        df = _fetch_csv(url)
    except DataError:
        # fall back to cache if we got throttled or errored
        return _read_cache(cp, parse_dates=["date"])

    # Expected columns: timestamp, open, high, low, close, volume
    if "timestamp" not in df.columns or "close" not in df.columns:
        raise DataError(f"Unexpected CSV schema from Alpha Vantage for {symbol}: {df.columns.tolist()}")

    df = df.rename(columns={"timestamp": "date"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["date", "close"]).sort_values("date")
    df["symbol"] = symbol
    df = df[["date", "close", "symbol"]]
    df.to_csv(cp, index=False)
    return df

def get_prices(symbols=None) -> pd.DataFrame:
    symbols = symbols or TICKERS_DEFAULT
    frames = [fetch_daily(s) for s in symbols]
    return pd.concat(frames, ignore_index=True)

def normalize_to_100(prices: pd.DataFrame) -> pd.DataFrame:
    df = prices.sort_values(["symbol", "date"]).copy()
    df["norm"] = df.groupby("symbol")["close"].transform(lambda s: 100 * s / s.iloc[0])
    return df[["date", "symbol", "norm"]]

def _fetch_daily_ohlc(symbol: str, force: bool = False) -> pd.DataFrame:
    """OHLC CSV -> date, open, high, low, close, symbol."""
    cp = _ohlc_cache_path(symbol)

    if not force and os.path.exists(cp):
        return _read_cache(cp, parse_dates=["date"])

    if not API_KEY:
        return _read_cache(cp, parse_dates=["date"])

    url = (f"{BASE}?function=TIME_SERIES_DAILY&symbol={symbol}"
           f"&outputsize=full&datatype=csv&apikey={API_KEY}")

    try:
        df = _fetch_csv(url)
    except DataError:
        return _read_cache(cp, parse_dates=["date"])

    if "timestamp" not in df.columns or not {"open","high","low","close"}.issubset(df.columns):
        raise DataError(f"Unexpected CSV schema (OHLC) for {symbol}: {df.columns.tolist()}")

    df = df.rename(columns={"timestamp": "date"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["open","high","low","close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date","open","high","low","close"]).sort_values("date")
    df["symbol"] = symbol
    df = df[["date", "open", "high", "low", "close", "symbol"]]
    df.to_csv(cp, index=False)
    return df

def fetch_daily_ohlc(symbol: str, force: bool = False) -> pd.DataFrame:
    return _fetch_daily_ohlc(symbol, force=force)

def get_ohlc(symbol: str) -> pd.DataFrame:
    return fetch_daily_ohlc(symbol)
