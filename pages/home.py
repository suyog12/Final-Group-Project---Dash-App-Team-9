from dash import html, dcc, register_page
from flask import session
import dash

register_page(__name__, path="/home", name="Home")

_content = html.Div(id="home", children=[
    html.Section(id="home-intro", children=[
        html.Div(className="column", id = "title", children=[
            html.H2("Change Your Stock Porfolio"),
            html.H3("Learn from the past to predict the future")
        ]),
        html.Div(className="column", id="title-content-aside", children=[
            html.H4("Have you ever wondered..."),
            html.Ul([
                html.Li("what if I invested $100 before a company took off?"),
                html.Li("What signs should I have looked for to see that they were about to make it big?")
            ]),
        ]),
        html.P("We have data on over 100 large companies -- big in the stock market. We have analyzed their historical trends, investigated their history and the state of world then, and predict how their stock is likely to behave based on statistical analysis and current events."),
        html.P("More bragging and yes we are a very serious company you want to give us your money")
    ]),
    html.Section(id="home-cards", className="cards", children=[
        html.Div(className="card", children=[
            html.H3("The $100 Question"),
            html.P("Track $100 growing over time. Toggle tickers and choose dates."),
            dcc.Link("Open", href="/hundred", className="btn")
        ]),
        html.Div(className="card", children=[
            html.H3("Running the Risks"),
            html.P("Explore rolling volatility (risk). Adjust the window length."),
            dcc.Link("Open", href="/risks", className="btn")
        ]),
    ]),
])

def layout():
    if not session.get("user"):
        return dcc.Location(pathname="/login?next=/home", id="home-redirect")
    return _content
