from dash import html, dcc, register_page, callback, Input, Output
from flask import session
import plotly.graph_objects as go
import pandas as pd

from utils.data import get_ohlc, TICKERS_DEFAULT

register_page(__name__, path="/activity", name="Daily Trading Activity")

SEED = get_ohlc(TICKERS_DEFAULT[0])
MIN_D, MAX_D = SEED["date"].min(), SEED["date"].max()
TODAY = pd.Timestamp.today().normalize()
DEFAULT_END = min(TODAY, MAX_D)
DEFAULT_START = max(MIN_D, DEFAULT_END - pd.Timedelta(days=60))

controls = html.Div(
    id="rk-controls",
    children=[
        html.Div(
            className="control",
            children=[
                html.Label("Ticker", htmlFor="rk-ticker"),
                dcc.Dropdown(
                    id="rk-ticker",
                    options=[{"label": t, "value": t} for t in TICKERS_DEFAULT],
                    value=TICKERS_DEFAULT[0],
                    clearable=False,
                ),
            ],
        ),
        html.Div(
            className="control",
            children=[
                html.Label("Date Range", htmlFor="rk-dates"),
                dcc.DatePickerRange(
                    id="rk-dates",
                    min_date_allowed=MIN_D,
                    max_date_allowed=MAX_D,
                    start_date=DEFAULT_START.date(),
                    end_date=DEFAULT_END.date(),
                    display_format="MM-DD-YYYY",
                ),
            ],
        ),
    ],
)

def layout():
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/activity", id="rk-redirect")

    return html.Div(
        id="rk-page",
        children=[
            html.Section(
                id="rk-header",
                className="page",
                children=[
                    html.H2("Daily Trading Activity"),
                    html.P("Interactive daily candlesticks with 20/50 day moving averages."),
                ],
            ),
            html.Section(
                id="rk-body",
                className="page",
                children=[
                    html.Aside(id="rk-sidebar", children=[controls]),
                    html.Section(
                        id="rk-content",
                        children=[
                            dcc.Graph(
                                id="rk-chart",
                                config={"displayModeBar": True},
                                style={"height": "72vh"},
                            )
                        ],
                    ),
                ],
            ),
        ],
    )

@callback(
    Output("rk-chart", "figure"),
    Input("rk-ticker", "value"),
    Input("rk-dates", "start_date"),
    Input("rk-dates", "end_date"),
)
def update_chart(ticker, start_date, end_date):
    df = get_ohlc(ticker).copy()
    tmin, tmax = df["date"].min(), df["date"].max()

    if not start_date or not end_date:
        end_date = min(pd.Timestamp.today().normalize(), tmax)
        start_date = max(tmin, end_date - pd.Timedelta(days=60))

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    start_date, end_date = max(start_date, tmin), min(end_date, tmax)

    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()

    y_min, y_max = float(df["low"].min()), float(df["high"].max())
    pad = max(1.0, (y_max - y_min) * 0.05)

    candle = go.Candlestick(
        x=df["date"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name=ticker,
        whiskerwidth=0.45,
        increasing=dict(line=dict(color="#2e8b57", width=1.6)),
        decreasing=dict(line=dict(color="#c23b22", width=1.6)),
        showlegend=True,
    )
    ma20 = go.Scatter(x=df["date"], y=df["MA20"], mode="lines", name="MA 20",
                      line=dict(width=2.0, color="#1f77b4"))
    ma50 = go.Scatter(x=df["date"], y=df["MA50"], mode="lines", name="MA 50",
                      line=dict(width=2.0, color="#ff7f0e"))

    fig = go.Figure(data=[candle, ma20, ma50])
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(255,255,255,.7)"),
        xaxis=dict(
            type="date",
            rangeslider=dict(visible=True, thickness=0.08),
            showgrid=True, gridcolor="rgba(0,0,0,0.07)",
            tickformat="%b %Y",
            rangebreaks=[dict(bounds=["sat", "mon"])],
        ),
        yaxis=dict(
            title="Price (USD)",
            range=[y_min - pad, y_max + pad],
            showgrid=True, gridcolor="rgba(0,0,0,0.07)",
        ),
    )
    return fig
