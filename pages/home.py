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
                                    html.H3("Learn from the past to predict the future"),
                                    html.P(
                                        "We analyze historical trends across 100+ large companies "
                                        "and replay simple ‘what if’ scenarios so you can learn "
                                        "patterns before you invest."
                                    ),
                                    html.Div(
                                        className="home-cta",
                                        children=[
                                            dcc.Link("Login", href="/login", className="btn"),
                                            dcc.Link("Sign up", href="/signup", className="btn"),
                                        ],
                                    ),
                                ],
                            ),
                            html.Aside(
                                className="home-right",
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
