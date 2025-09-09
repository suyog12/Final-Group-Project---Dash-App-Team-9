# pages/volatility.py
from dash import html, dcc, register_page, callback, Input, Output
from flask import session
import plotly.express as px
import pandas as pd

from utils.data import get_prices, TICKERS_DEFAULT

register_page(__name__, path="/volatility", name="Volatility")

# pull close-only prices once (cached by your data utils)
PRICES_ALL = get_prices(TICKERS_DEFAULT)

# sensible default dates: last ~12 months within available data
T_MIN = PRICES_ALL["date"].min()
T_MAX = PRICES_ALL["date"].max()
TODAY = pd.Timestamp.today().normalize()
DEFAULT_END = min(TODAY, T_MAX)
DEFAULT_START = max(T_MIN, DEFAULT_END - pd.Timedelta(days=365))

controls = html.Div(id="vol-controls", children=[
    html.Div(className="control", children=[
        html.Label("Tickers", htmlFor="vol-tickers"),
        dcc.Checklist(
            id="vol-tickers",
            value=TICKERS_DEFAULT,
            options=[{"label": t, "value": t} for t in TICKERS_DEFAULT],
            inline=True,
        ),
    ]),
    html.Div(className="control", children=[
        html.Label("Date Range", htmlFor="vol-dates"),
        dcc.DatePickerRange(
            id="vol-dates",
            min_date_allowed=T_MIN,
            max_date_allowed=T_MAX,
            start_date=DEFAULT_START.date(),
            end_date=DEFAULT_END.date(),
            display_format="YYYY-MM-DD",
        ),
    ]),
    html.Div(className="control", children=[
        html.Label("Rolling Window (trading days)", htmlFor="vol-window"),
        dcc.Slider(
            id="vol-window",
            min=10, max=120, step=5, value=30,
            marks={10: "10", 30: "30", 60: "60", 90: "90", 120: "120"},
            tooltip={"placement": "bottom", "always_visible": False},
        ),
    ]),
])

_page = html.Div(id="vol-page", children=[
    html.Section(id="vol-header", children=[
        html.H2("Volatility"),
        html.P("30-day rolling annualized volatility (adjustable window)."),
    ]),
    html.Section(id="vol-body", children=[
        html.Aside(id="vol-sidebar", children=[controls]),
        html.Section(id="vol-content", children=[
            dcc.Graph(id="vol-chart", config={"displayModeBar": "hover"}, style={"height": "72vh"}),
        ]),
    ]),
])

def layout():
    # gate access like your other pages
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/volatility", id="vol-redirect")
    return _page


@callback(
    Output("vol-chart", "figure"),
    Input("vol-tickers", "value"),
    Input("vol-dates", "start_date"),
    Input("vol-dates", "end_date"),
    Input("vol-window", "value"),
)
def update_vol_chart(tickers, start_date, end_date, window):
    if not tickers:
        # empty chart prompt
        return px.area(title="Select at least one ticker")

    # filter by tickers + date window
    df = PRICES_ALL[PRICES_ALL["symbol"].isin(tickers)].copy()
    if start_date and end_date:
        s, e = pd.to_datetime(start_date), pd.to_datetime(end_date)
        df = df[(df["date"] >= s) & (df["date"] <= e)]

    # compute rolling annualized volatility
    df = df.sort_values(["symbol", "date"])
    df["ret"] = df.groupby("symbol")["close"].pct_change()
    ann = 252 ** 0.5
    df["roll_vol"] = (
        df.groupby("symbol")["ret"]
          .rolling(window, min_periods=window)
          .std()
          .reset_index(level=0, drop=True) * ann
    )
    vol = df.dropna(subset=["roll_vol"])[["date", "symbol", "roll_vol"]]
    
    custom_colors = ["#2964b4", "#b24b7b"] # changes the colors of the graph
    fig = px.area(
        vol, x="date", y="roll_vol", color="symbol",
        labels={"roll_vol": "Annualized Volatility", "date": "date", "symbol": "Ticker"},
        template="plotly_white", color_discrete_sequence=custom_colors,
    )
    fig.update_layout(
        title="Rolling Volatility",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=40, r=20, t=85, b=40),
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(rangeslider_visible=True)

    return fig
