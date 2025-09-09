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
                                    html.Li("What signs could I have spotted before the big run?"),
                                    html.Li("How do I choose my portfolio stocks?"),
                                    html.Li("What are all these terms being thrown around like volatility, diversification, and liquidity?"),
                                    html.Li("What if I invested $100 before a company took off?", style={"color":"#145b4b", "font-weight":"bold"}),
                                ]
                            ),
                        ],
                    ),
                    html.P("In 2025, we decided that one of the main problems facing working professionals was that learning the details of the stock market took too long. We're here to help you navigate this tumultous market by guiding you through the ins and outs with stock analysis conducted by our professionals."),
                    html.P("We have taken data from Microsoft and Apple, using [INSERT NAME] API, with more on the way. In order to make future trends more understandable, we have investigated and explained their historical trends in order to predict how their stock is likely to behave based on statistical analysis and current events."),
                    html.P("Use the navbar or click one of the below buttons in order to access our growing library of visualizations for stock analysis and kick off your investment journey today."),
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
