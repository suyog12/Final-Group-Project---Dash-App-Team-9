from dash import html, dcc, register_page
from flask import session

register_page(__name__, path="/dashboard", name="Dashboard")

def layout():
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/dashboard", id="dash-redirect")

    return html.Div(
        id="dashboard",
        children=[
            html.Section(
                className="page",
                children=[
                    html.H1("Change Your Stock Portfolio"),
                    html.H3("Learn from the past to predict the future"),
                    html.P(
                        "We analyze historical trends across 100+ large companies and replay simple "
                        "‘what if’ scenarios so you can learn patterns before you invest."
                    ),
                    html.Div(
                        className="dash-wonder",
                        children=[
                            html.H4("Have you ever wondered..."),
                            html.Ul(
                                [
                                    html.Li("What if I invested $100 before a company took off?"),
                                    html.Li("What signs could I have spotted before the big run?"),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="page",
                children=[
                    html.Div(
                        className="cards",
                        children=[
                            html.Div(
                                className="card",
                                children=[
                                    html.H3("The $100 Question"),
                                    html.P("Track $100 growing over time. Toggle tickers and choose dates."),
                                    dcc.Link("Open", href="/hundred", className="btn"),
                                ],
                            ),
                            html.Div(
                                className="card",
                                children=[
                                    html.H3("Daily Trading Activity"),
                                    html.P("Explore daily OHLC action via interactive candlesticks."),
                                    dcc.Link("Open", href="/activity", className="btn"),
                                ],
                            ),
                            html.Div(
                                className="card",
                                children=[
                                    html.H3("Volatility"),
                                    html.P("Rolling risk metrics (coming soon)."),
                                    dcc.Link("Open", href="/volatility", className="btn"),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
    )
