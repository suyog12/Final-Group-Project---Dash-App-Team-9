# utils/data.py
import os
from datetime import datetime
import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")
TICKERS_DEFAULT = ["AAPL", "MSFT"]
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class DataError(Exception):
    pass

def _cache_path(symbol: str) -> str:
    return os.path.join(CACHE_DIR, f"{symbol}_daily.csv")

def fetch_daily(symbol: str, force: bool = False) -> pd.DataFrame:
    """Fetch full daily data, cache to CSV; if no key, try cache first."""
    cp = _cache_path(symbol)

    # if not forcing and cache exists, use it (works offline / no key)
    if not force and os.path.exists(cp):
        return pd.read_csv(cp, parse_dates=["date"])

    if not API_KEY:
        raise DataError("Missing ALPHAVANTAGE_API_KEY env var and no cache found.")

    url = (
        f"{BASE}?function=TIME_SERIES_DAILY&symbol={symbol}"
        f"&outputsize=full&datatype=csv&apikey={API_KEY}"
    )
    df = pd.read_csv(url)
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

def rolling_volatility(prices: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    df = prices.sort_values(["symbol", "date"]).copy()
    df["ret"] = df.groupby("symbol")["close"].pct_change()
    ann = 252 ** 0.5
    df["roll_vol"] = (
        df.groupby("symbol")["ret"]
          .rolling(window, min_periods=window)
          .std()
          .reset_index(level=0, drop=True) * ann
    )
    return df.dropna(subset=["roll_vol"])[["date", "symbol", "roll_vol"]]
