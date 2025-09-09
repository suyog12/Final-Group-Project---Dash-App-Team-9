# pages/risks.py
from dash import html, dcc, register_page, callback, Input, Output
from flask import session
import plotly.graph_objects as go
import pandas as pd

from utils.data import get_ohlc, TICKERS_DEFAULT

register_page(__name__, path="/risks", name="Running the Risks")

# Seed from the first ticker to configure the initial date picker bounds
SEED_TICKER = TICKERS_DEFAULT[0]
_SEED = get_ohlc(SEED_TICKER)

SEED_MIN = _SEED["date"].min()
SEED_MAX = _SEED["date"].max()

# Default to "now" (UTC-normalized) but never beyond available data
TODAY = pd.Timestamp.today().normalize()
DEFAULT_END = min(TODAY, SEED_MAX)
DEFAULT_START = max(SEED_MIN, DEFAULT_END - pd.Timedelta(days=60))  # ~2 months

controls = html.Div(id="rk-controls", children=[
    html.Div(className="control", children=[
        html.Label("Ticker", htmlFor="rk-ticker"),
        dcc.Dropdown(
            id="rk-ticker",
            options=[{"label": t, "value": t} for t in TICKERS_DEFAULT],
            value=SEED_TICKER,
            clearable=False,
        ),
    ]),
    html.Div(className="control", children=[
        html.Label("Date Range", htmlFor="rk-dates"),
        dcc.DatePickerRange(
            id="rk-dates",
            min_date_allowed=SEED_MIN,
            max_date_allowed=SEED_MAX,
            start_date=DEFAULT_START.date(),
            end_date=DEFAULT_END.date(),
            display_format="YYYY-MM-DD",
        ),
    ]),
])

_page = html.Div(id="rk-page", children=[
    html.Section(id="rk-header", children=[
        html.H2("Rolling Volatility (Risk)"),
        html.P("A candlestick view of daily price action. Wider candles and long wicks often indicate higher volatility."),
    ]),
    html.Section(id="rk-body", children=[
        html.Aside(id="rk-sidebar", children=[controls]),
        html.Section(id="rk-content", children=[
            dcc.Graph(id="rk-chart", config={"displayModeBar": True}, style={"height": "72vh"}),
        ]),
    ]),
])

def layout():
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/risks", id="rk-redirect")
    return _page


@callback(
    Output("rk-chart", "figure"),
    Input("rk-ticker", "value"),
    Input("rk-dates", "start_date"),
    Input("rk-dates", "end_date"),
)
def update_chart(ticker, start_date, end_date):
    df = get_ohlc(ticker).copy()

    # If no dates are provided (first render or cleared), use "last ~2 months up to today",
    # clipped to this ticker's data span.
    t_min, t_max = df["date"].min(), df["date"].max()
    today = pd.Timestamp.today().normalize()
    end_default = min(today, t_max)
    start_default = max(t_min, end_default - pd.Timedelta(days=60))

    if not start_date or not end_date:
        start_date, end_date = start_default, end_default

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Clip to available range just in case
    start_date = max(start_date, t_min)
    end_date = min(end_date, t_max)

    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # Moving averages for trend context
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()

    # Y padding so candles don't hug the edges
    y_min, y_max = float(df["low"].min()), float(df["high"].max())
    pad = max(1.0, (y_max - y_min) * 0.05)

    candle = go.Candlestick(
        x=df["date"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name=ticker,
        whiskerwidth=0.45,
        increasing=dict(line=dict(color="#2e8b57", width=1.6)),
        decreasing=dict(line=dict(color="#c23b22", width=1.6)),
    )

    ma20 = go.Scatter(
        x=df["date"], y=df["MA20"], mode="lines", name="MA 20",
        line=dict(width=1.8, color="#1f77b4"),
    )
    ma50 = go.Scatter(
        x=df["date"], y=df["MA50"], mode="lines", name="MA 50",
        line=dict(width=1.8, color="#ff7f0e"),
    )

    fig = go.Figure(data=[candle, ma20, ma50])
    fig.update_layout(
        template="plotly_white",
        title=f"{ticker} — Daily Candlestick (last ~2 months by default)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            type="date",
            rangeslider=dict(visible=True, thickness=0.08),
            showgrid=True, gridcolor="rgba(0,0,0,0.07)",
            tickformat="%b %Y",
            rangebreaks=[dict(bounds=["sat", "mon"])],  # hide weekends
        ),
        yaxis=dict(
            title="Price (USD)",
            range=[y_min - pad, y_max + pad],
            showgrid=True, gridcolor="rgba(0,0,0,0.07)",
        ),
    )
    return fig
