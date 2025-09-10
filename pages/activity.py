from dash import html, dcc, register_page, callback, Input, Output
from flask import session
import plotly.graph_objects as go
import pandas as pd

from utils.data import get_ohlc, TICKERS_DEFAULT, DataError

register_page(__name__, path="/activity", name="Daily Trading Activity")

SEED_TICKER = TICKERS_DEFAULT[0]
TODAY = pd.Timestamp.today().normalize()

# Try to discover min/max from cached/remote data; otherwise default to a sane 2-month window
try:
    _seed = get_ohlc(SEED_TICKER)
    SEED_MIN, SEED_MAX = _seed["date"].min(), _seed["date"].max()
except Exception:
    SEED_MIN, SEED_MAX = TODAY - pd.Timedelta(days=60), TODAY

DEFAULT_END = min(TODAY, SEED_MAX)
DEFAULT_START = max(SEED_MIN, DEFAULT_END - pd.Timedelta(days=60))

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
                    value=SEED_TICKER,
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
                    min_date_allowed=SEED_MIN,
                    max_date_allowed=SEED_MAX,
                    start_date=DEFAULT_START.date(),
                    end_date=DEFAULT_END.date(),
                    display_format="MM-DD-YYYY",
                ),
            ],
        ),
    ],
)

def _message_figure(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        annotations=[dict(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font=dict(size=16))],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig

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
                    html.P("Interactive chart to explore how your investments would fluctuate day-to-day in price. Experience how they react to daily market swings, and visualize highs, lows, opens, and closes, using 20 day moving averages and 50 day moving averages.")
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
                                config={"displayModeBar": True, "displaylogo": False},
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
    # Try to load data for the selected ticker
    try:
        df = get_ohlc(ticker).copy()
    except (DataError, Exception):
        return _message_figure(
            "Price data is not available right now. "
            "If you're deploying on Render, consider pre-seeding the data_cache or retry later."
        )

    if df.empty or not {"date", "open", "high", "low", "close"}.issubset(df.columns):
        return _message_figure("No OHLC data available for this ticker/date range.")

    tmin, tmax = df["date"].min(), df["date"].max()
    # Default to the last ~2 months up to today (but clipped to available data)
    if not start_date or not end_date:
        end_date = min(pd.Timestamp.today().normalize(), tmax)
        start_date = max(tmin, end_date - pd.Timedelta(days=60))

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    start_date, end_date = max(start_date, tmin), min(end_date, tmax)

    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()
    if df.empty:
        return _message_figure("No data in the selected range. Try expanding the dates.")

    # Moving averages for trend context (MAs are plotted AFTER candles so they sit on top)
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
        increasing=dict(line=dict(color="#026633", width=1.6)),
        decreasing=dict(line=dict(color="#bf0940", width=1.6)),
        showlegend=True,
    )
    # Put MAs AFTER the candle so lines are clearly visible above candles
    ma20 = go.Scatter(
        x=df["date"], y=df["MA20"], mode="lines", name="MA 20",
        line=dict(width=2.0, color="#472bbd"),
        hovertemplate="MA 20: %{y:.2f}<extra></extra>"
    )
    ma50 = go.Scatter(
        x=df["date"], y=df["MA50"], mode="lines", name="MA 50",
        line=dict(width=2.0, color="#0a80ed"),
        hovertemplate="MA 50: %{y:.2f}<extra></extra>"
    )

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
            rangebreaks=[dict(bounds=["sat", "mon"])],  # hide weekends
        ),
        yaxis=dict(
            title="Price (USD)",
            range=[y_min - pad, y_max + pad],
            showgrid=True, gridcolor="rgba(0,0,0,0.07)",
        ),
        uirevision="activity",  # preserve zoom when changing props
    )
    return fig
