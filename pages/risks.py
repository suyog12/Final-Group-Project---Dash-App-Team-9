from dash import html, dcc, register_page, callback, Input, Output
import plotly.express as px
import pandas as pd
from utils.data import get_prices, rolling_volatility, TICKERS_DEFAULT

register_page(__name__, path="/risks", name="Running the Risks")

PRICES = get_prices(TICKERS_DEFAULT)

controls = html.Div(id="rk-controls", children=[
    html.Div(className="control", children=[
        html.Label("Tickers", htmlFor="rk-tickers"),
        dcc.Checklist(id="rk-tickers",
                      value=TICKERS_DEFAULT,
                      options=[{"label": t, "value": t} for t in TICKERS_DEFAULT],
                      inline=True),
    ]),
    html.Div(className="control", children=[
        html.Label("Rolling Window (trading days)", htmlFor="rk-window"),
        dcc.Slider(id="rk-window", min=10, max=120, step=5, value=30,
                   marks={10:"10",30:"30",60:"60",120:"120"}),
    ]),
    html.Div(className="control", children=[
        html.Label("Date Range", htmlFor="rk-dates"),
        dcc.DatePickerRange(
            id="rk-dates",
            min_date_allowed=PRICES["date"].min(),
            max_date_allowed=PRICES["date"].max(),
            start_date=PRICES["date"].min(),
            end_date=PRICES["date"].max(),
            display_format="YYYY-MM-DD",
        ),
    ]),
])

layout = html.Div(id="rk-page", children=[
    html.Section(id="rk-header", children=[
        html.H2("Rolling Volatility (Risk)"),
        html.P("Volatility is the rolling standard deviation of daily returns, annualized (~252 trading days). Higher = riskier."),
    ]),
    html.Section(id="rk-body", children=[
        html.Aside(id="rk-sidebar", children=[controls]),
        html.Section(id="rk-content", children=[
            dcc.Graph(id="rk-chart", config={"displayModeBar": False}),
        ]),
    ]),
])

@callback(
    Output("rk-chart", "figure"),
    Input("rk-tickers", "value"),
    Input("rk-window", "value"),
    Input("rk-dates", "start_date"),
    Input("rk-dates", "end_date"),
)
def update_chart(tickers, window, start_date, end_date):
    if not tickers:
        return px.line(title="Select at least one ticker")
    df = PRICES[PRICES["symbol"].isin(tickers)]
    df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
    vol = rolling_volatility(df, window)
    fig = px.line(vol, x="date", y="roll_vol", color="symbol",
                  labels={"roll_vol":"Annualized Volatility", "date":"date", "symbol":"Ticker"})
    fig.update_layout(hovermode="x unified", legend_title_text="Ticker")
    fig.update_xaxes(rangeslider_visible=True)
    return fig
