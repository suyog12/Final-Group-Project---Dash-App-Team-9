# pages/hundred_question.py
from dash import html, dcc, register_page, callback, Input, Output
from flask import session
import plotly.express as px
import pandas as pd

from utils.data import get_prices, normalize_to_100, TICKERS_DEFAULT

register_page(__name__, path="/hundred", name="The $100 Question")

# Pre-load
PRICES = get_prices(TICKERS_DEFAULT)               # date, close, symbol
NORM = normalize_to_100(PRICES)                    # date, symbol, norm

controls = html.Div(
    id="hq-controls",
    children=[
        html.Div(
            className="control",
            children=[
                html.Label("Tickers"),
                dcc.Checklist(
                    id="hq-tickers",
                    value=TICKERS_DEFAULT,
                    options=[{"label": t, "value": t} for t in TICKERS_DEFAULT],
                    inline=True,
                ),
            ],
        ),
        html.Div(
            className="control",
            children=[
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id="hq-dates",
                    min_date_allowed=NORM["date"].min(),
                    max_date_allowed=NORM["date"].max(),
                    start_date=NORM["date"].min(),
                    end_date=NORM["date"].max(),
                    display_format="MM-DD-YYYY",
                ),
            ],
        ),
        html.Div(
            className="control",
            children=[
                html.Label("Series"),
                dcc.RadioItems(
                    id="hq-series",
                    value="index",
                    options=[
                        {"label": "Index ($100 at first available)", "value": "index"},
                        {"label": "Invest $100 at range start", "value": "invest"},
                    ],
                    inline=True,
                ),
            ],
        ),
        html.Div(
            className="control",
            children=[
                dcc.Checklist(
                    id="hq-log",
                    options=[{"label": "Log scale", "value": "log"}],
                    value=[],
                    inline=True,
                )
            ],
        ),
    ],
)

_page = html.Div(
    id="hq-page",
    className="page",
    children=[
        html.Section(id="hq-header", children=[html.H2("If you invested $100…")]),
        html.Section(
            id="hq-body",
            children=[
                html.Aside(id="hq-sidebar", children=[controls]),
                html.Section(
                    id="hq-content",
                    children=[dcc.Graph(id="hq-chart", config={"displayModeBar": "hover"})],
                ),
            ],
        ),
    ],
)

def layout():
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/hundred", id="hq-redirect")
    return _page

def _invest_100_over_range(prices: pd.DataFrame, tickers, start_date, end_date) -> pd.DataFrame:
    """
    Rebase each ticker so the first available point *inside* the chosen
    range equals $100, then compound forward.
    Returns columns: date, symbol, val_100
    """
    df = prices[prices["symbol"].isin(tickers)].copy()
    # clip to selected window (if user picks a weekend, we start from first trading date >= start_date)
    s = pd.to_datetime(start_date) if start_date else df["date"].min()
    e = pd.to_datetime(end_date) if end_date else df["date"].max()
    df = df[(df["date"] >= s) & (df["date"] <= e)].sort_values(["symbol", "date"])

    # returns computed *within* the window
    df["ret"] = df.groupby("symbol")["close"].pct_change()
    df["ret"] = df["ret"].fillna(0.0)  # first point in range => 0% so it stays at 100
    idx = (1.0 + df["ret"]).groupby(df["symbol"]).cumprod()
    df["val_100"] = 100.0 * idx
    return df[["date", "symbol", "val_100"]]

@callback(
    Output("hq-chart", "figure"),
    Input("hq-tickers", "value"),
    Input("hq-dates", "start_date"),
    Input("hq-dates", "end_date"),
    Input("hq-series", "value"),
    Input("hq-log", "value"),
)
def update_chart(tickers, start_date, end_date, series_mode, log_value):
    if not tickers:
        return px.line(title="Select at least one ticker")

    custom_colors = ["#2964b4", "#b24b7b"]  # your palette

    if series_mode == "invest":
        # Rebase within the selected range -> “accumulative” $100 chart
        cum = _invest_100_over_range(PRICES, tickers, start_date, end_date)
        fig = px.line(
            cum,
            x="date",
            y="val_100",
            color="symbol",
            labels={"val_100": "Value of $100 ($)", "date": "date", "symbol": "Ticker"},
            color_discrete_sequence=custom_colors,
        )
    else:
        # Legacy index ($100 at first available date overall)
        df = NORM[NORM["symbol"].isin(tickers)].copy()
        if start_date and end_date:
            df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        fig = px.line(
            df,
            x="date",
            y="norm",
            color="symbol",
            labels={"norm": "Index ($100 start)", "date": "date", "symbol": "Ticker"},
            color_discrete_sequence=custom_colors,
        )

    fig.update_layout(
        hovermode="x unified",
        legend_title_text="Ticker",
        template="plotly_white",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    fig.update_xaxes(rangeslider_visible=True)

    if "log" in (log_value or []):
        fig.update_yaxes(type="log")

    return fig
