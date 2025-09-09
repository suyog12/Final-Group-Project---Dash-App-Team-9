import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Alpha Vantage config
BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")

# Defaults / cache
TICKERS_DEFAULT = ["AAPL", "MSFT"]
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class DataError(Exception):
    """Raised when data cannot be fetched and no cache exists."""
    pass


# ---------------------------
# Close-only (for index/vol)
# ---------------------------
def _cache_path(symbol: str) -> str:
    return os.path.join(CACHE_DIR, f"{symbol}_daily.csv")


def fetch_daily(symbol: str, force: bool = False) -> pd.DataFrame:
    """
    Fetch full daily series (CSV) for a symbol and cache it.
    Returns columns: date, close, symbol
    """
    cp = _cache_path(symbol)
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
    """
    Index each symbol to 100 at its first available date.
    Returns: date, symbol, norm
    """
    df = prices.sort_values(["symbol", "date"]).copy()
    df["norm"] = df.groupby("symbol")["close"].transform(lambda s: 100 * s / s.iloc[0])
    return df[["date", "symbol", "norm"]]


def rolling_volatility(prices: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Rolling annualized volatility from daily close-to-close returns.
    Returns: date, symbol, roll_vol
    """
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


# ---------------------------
# OHLC (for candlesticks)
# ---------------------------
def _ohlc_cache_path(symbol: str) -> str:
    return os.path.join(CACHE_DIR, f"{symbol}_daily_ohlc.csv")


def fetch_daily_ohlc(symbol: str, force: bool = False) -> pd.DataFrame:
    """
    Fetch full daily OHLC (CSV) for a symbol and cache it.
    Returns columns: date, open, high, low, close, symbol
    """
    cp = _ohlc_cache_path(symbol)
    if not force and os.path.exists(cp):
        return pd.read_csv(cp, parse_dates=["date"])

    if not API_KEY:
        raise DataError("Missing ALPHAVANTAGE_API_KEY env var and no OHLC cache found.")

    url = (
        f"{BASE}?function=TIME_SERIES_DAILY&symbol={symbol}"
        f"&outputsize=full&datatype=csv&apikey={API_KEY}"
    )
    df = pd.read_csv(url)
    df = df.rename(columns={"timestamp": "date"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date", "open", "high", "low", "close"]).sort_values("date")
    df["symbol"] = symbol
    df = df[["date", "open", "high", "low", "close", "symbol"]]
    df.to_csv(cp, index=False)
    return df


def get_ohlc(symbol: str) -> pd.DataFrame:
    """Convenience wrapper: return cached OHLC for one symbol."""
    return fetch_daily_ohlc(symbol)
