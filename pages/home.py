from dash import html, dcc, register_page
from flask import session

register_page(__name__, path="/home", name="Home")

def layout():
    if session.get("user"):
        return dcc.Location(pathname="/dashboard", id="home-redirect")

    return html.Div(
        id="home",
        children=[
            html.Section(
                className="page",
                children=[
                    html.Div(
                        className="home-hero",
                        children=[
                            html.Div(
                                className="home-left",
                                children=[
                                    html.H1("Change Your Stock Portfolio"),
                                    html.H3("Learn from the past to predict the future with A9 Solutions"),
                                    html.P(
                                        "We analyze historical trends across 100+ large companies "
                                        "and replay simple ‘what if’ scenarios so you can learn "
                                        "patterns before you invest."
                                    ),
                                ],
                            ),
                            html.Aside(
                                className="home-right",
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
                        ],
                    ),
                    html.Hr(),
                    html.Div(
                        children=[
                            html.P("In 2025, we decided that one of the main problems facing working professionals was that learning the details of the stock market took too long. We're here to help you navigate this tumultous market by guiding you through the ins and outs with stock analysis conducted by our professionals."),
                            html.P("We have taken data from Microsoft and Apple, using the reputable Alpha Vantage's Time Series Daily API, with more on the way. In order to make future trends more understandable, we have investigated and explained their historical trends in order to predict how their stock is likely to behave based on statistical analysis and current events."),
                            html.P("Sign up in order to access our growing library of visualizations for stock analysis and kick off your investment journey today."),
                            html.Div(
                                className="home-cta",
                                children=[
                                    dcc.Link("Login", href="/login", className="btn"),
                                    dcc.Link("Sign up", href="/signup", className="btn"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="page",
                children=[
                    html.H2("Know the Founders"),
                    html.Img(src="/assets/images/founders-group.png",
                             className="founders-group", alt="Founders"),
                    html.Div(
                        className="founder-grid",
                        children=[
                            html.Div(
                                className="founder-card",
                                children=[
                                    html.Strong("Bryce"),
                                    html.P("Frontend & user experience."),
                                    html.Img(src="/assets/images/founder-bryce.jpg",
                                             alt="Bryce headshot",
                                             className="founder-pop"),
                                ],
                            ),                            
                            html.Div(
                                className="founder-card",
                                children=[
                                    html.Strong("Suyog"),
                                    html.P("Quant research & backtests."),
                                    html.Img(src="/assets/images/founder-suyog.jpg",
                                             alt="Suyog headshot",
                                             className="founder-pop"),
                                ],
                            ),
                            html.Div(
                                className="founder-card",
                                children=[
                                    html.Strong("Luke"),
                                    html.P("Data modeling & infrastructure."),
                                    html.Img(src="/assets/images/founder-luke.jpg",
                                             alt="Luke headshot",
                                             className="founder-pop"),
                                ],
                            ),
                            html.Div(
                                className="founder-card",
                                children=[
                                    html.Strong("Vanessa"),
                                    html.P("Product & storytelling."),
                                    html.Img(src="/assets/images/founder-vanessa.jpg",
                                             alt="Vanessa headshot",
                                             className="founder-pop"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
