from dash import html, dcc, register_page, callback, Input, Output
from flask import session
import plotly.express as px
import pandas as pd
from utils.data import get_prices, normalize_to_100, TICKERS_DEFAULT

register_page(__name__, path="/hundred", name="The $100 Question")

PRICES = get_prices(TICKERS_DEFAULT)
NORM = normalize_to_100(PRICES)

controls = html.Div(
    id="hq-controls",
    children=[
        html.Div(className="control", children=[html.Label("Tickers"), dcc.Checklist(
            id="hq-tickers", value=TICKERS_DEFAULT, options=[{"label": t, "value": t} for t in TICKERS_DEFAULT], inline=True
        )]),
        html.Div(className="control", children=[html.Label("Date Range"), dcc.DatePickerRange(
            id="hq-dates",
            min_date_allowed=NORM["date"].min(),
            max_date_allowed=NORM["date"].max(),
            start_date=NORM["date"].min(),
            end_date=NORM["date"].max(),
            display_format="MM-DD-YYYY",
        )]),
        html.Div(className="control", children=[dcc.Checklist(
            id="hq-log", options=[{"label": "Log scale", "value": "log"}], value=[], inline=True
        )]),
    ],
)

_page = html.Div(
    id="hq-page",
    className="page",
    children=[
        html.Section(id="hq-header", children=[html.H2("If you invested $100…")]),
        html.Section(
            id="hq-body",
            children=[html.Aside(id="hq-sidebar", children=[controls]), html.Section(id="hq-content", children=[dcc.Graph(id="hq-chart", config={"displayModeBar": "hover"})])],
        ),
    ],
)

def layout():
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/hundred", id="hq-redirect")
    return _page

@callback(
    Output("hq-chart", "figure"),
    Input("hq-tickers", "value"),
    Input("hq-dates", "start_date"),
    Input("hq-dates", "end_date"),
    Input("hq-log", "value"),
)
def update_chart(tickers, start_date, end_date, log_value):
    if not tickers:
        return px.line(title="Select at least one ticker")
    df = NORM[NORM["symbol"].isin(tickers)]
    if start_date and end_date:
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
    custom_colors = ["#2964b4", "#b24b7b"] # changes the colors of the graph
    fig = px.line(df, x="date", y="norm", color="symbol", labels={"norm": "Index ($100 start)"}, color_discrete_sequence=custom_colors)
    fig.update_layout(hovermode="x unified", legend_title_text="Ticker", template="plotly_white")
    fig.update_xaxes(rangeslider_visible=True)
    if "log" in (log_value or []):
        fig.update_yaxes(type="log")
    return fig
