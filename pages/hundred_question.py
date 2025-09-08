from dash import html, dcc, register_page, callback, Input, Output
import plotly.express as px
import pandas as pd
from utils.data import get_prices, normalize_to_100, TICKERS_DEFAULT

register_page(__name__, path="/hundred", name="The $100 Question")

PRICES = get_prices(TICKERS_DEFAULT)
NORM = normalize_to_100(PRICES)

controls = html.Div(id="hq-controls", children=[
    html.Div(className="control", children=[
        html.Label("Tickers", htmlFor="hq-tickers"),
        dcc.Checklist(id="hq-tickers",
                      value=TICKERS_DEFAULT,
                      options=[{"label": t, "value": t} for t in TICKERS_DEFAULT],
                      inline=True),
    ]),
    html.Div(className="control", children=[
        html.Label("Date Range", htmlFor="hq-dates"),
        dcc.DatePickerRange(
            id="hq-dates",
            min_date_allowed=NORM["date"].min(),
            max_date_allowed=NORM["date"].max(),
            start_date=NORM["date"].min(),
            end_date=NORM["date"].max(),
            display_format="YYYY-MM-DD",
        ),
    ]),
    html.Div(className="control", children=[
        dcc.Checklist(id="hq-log",
                      options=[{"label": "Log scale", "value": "log"}],
                      value=[],
                      inline=True),
    ]),
])

layout = html.Div(id="hq-page", children=[
    html.Section(id="hq-header", children=[
        html.H2("If you invested $100…"),
        html.P("Indexing both stocks to $100 on their first available date makes the lines directly comparable."),
    ]),
    html.Section(id="hq-body", children=[
        html.Aside(id="hq-sidebar", children=[controls]),
        html.Section(id="hq-content", children=[
            dcc.Graph(id="hq-chart", config={"displayModeBar": False}),
        ]),
    ]),
])

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
    fig = px.line(df, x="date", y="norm", color="symbol",
                  labels={"norm":"Index ($100 start)", "date":"date", "symbol":"Ticker"})
    fig.update_layout(hovermode="x unified", legend_title_text="Ticker")
    fig.update_xaxes(rangeslider_visible=True)
    if "log" in (log_value or []):
        fig.update_yaxes(type="log")
    return fig
