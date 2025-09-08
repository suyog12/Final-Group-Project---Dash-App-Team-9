import pandas as pd
import plotly.express as px
from plotly.offline import plot as plot_offline

#API from https://www.alphavantage.co/documentation/ use TIME SERIES DAILY FREE API (25 USES PER DAY LIMIT)
API_KEY = "insert_api_key_here"

BASE = "https://www.alphavantage.co/query"
TICKERS = ["AAPL", "MSFT"]

##chatgpt used to help import data
def fetch(symbol: str) -> pd.DataFrame:
    url = (f"{BASE}?function=TIME_SERIES_DAILY"
           f"&symbol={symbol}&outputsize=full&datatype=csv&apikey={API_KEY}")
    df = pd.read_csv(url)

#basic clean, renaming, drop na, converts to numeric
    df = df.rename(columns={"timestamp": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"])
    df["symbol"] = symbol
    return df[["date", "close", "symbol"]]

#add both stock ticker prices to one dataset    
frames = [fetch(sym) for sym in TICKERS]
prices = pd.concat(frames, ignore_index=True)

#normalized prices, chatgpt help 
#normalizes price start at $100, both tickers start at same value, answers what if
norm = prices.copy()
norm["norm"] = (
    norm.groupby("symbol")["close"]
        .transform(lambda s: 100 * s / s.iloc[0])
)
norm = norm[["date", "norm", "symbol"]]

#interactive line chart- prices
fig_prices = px.line(
    norm, x="date", y="norm", color="symbol",
    title="Investing $100 Comparison",
    labels={"norm": "Index ($)", "date": "Date", "symbol": "Ticker"}
)
##add interactive features - hover and date range slider
fig_prices.update_layout(hovermode="x unified")
fig_prices.update_xaxes(rangeslider_visible=True)

##open local html file
price_graph = plot_offline(fig_prices, filename="prices_aapl_msft.html", auto_open=True)

#rolling volatility calculation from prices, chatgpt help
WINDOW = 30  #30 trading days to measure risk         
ANN = 252 ** 0.5 #annualize daily volatility by taking square root of 252, number of trading days per year

prices = prices.sort_values(["symbol", "date"])
prices["ret"] = prices.groupby("symbol")["close"].pct_change() #day to day percent change in trading return
##computing rolling volatility
prices["roll_vol"] = (
    prices.groupby("symbol")["ret"]
          .rolling(WINDOW, min_periods=WINDOW)
          .std()
          .reset_index(level=0, drop=True) * ANN)
vol = prices.loc[prices["roll_vol"].notna(), ["date", "symbol", "roll_vol"]]
##interactive line chart generations
fig_volatility = px.line(
    vol, x="date", y="roll_vol", color="symbol",
    title="Investing $100 Risk",
    labels={"roll_vol": "Index", "date": "Date", "symbol": "Ticker"}
)
##interactive features
fig_volatility.update_layout(hovermode="x unified")
fig_volatility.update_xaxes(rangeslider_visible=True)
##open html file
vol_graph= plot_offline(fig_volatility, filename="vol_aapl_msft.html", auto_open=True)
