from dash import html, dcc, register_page
register_page(__name__, path="/")

layout = html.Div(id="home",
    children=[
        html.Section(id="home-intro", children=[
            html.H2("Have you ever wondered: what if I invested $100 before a company took off?"),
            html.P("We can't predict the next big stock, but we can replay a simple 'what if'. "
                   "Use the tabs to compare Apple and Microsoft—growth on the $100 scale and the risk you would've taken.")
        ]),
        html.Section(id="home-cards", children=[
            html.Div(className="card", children=[
                html.H3("The $100 Question"),
                html.P("Track $100 growing over time. Toggle tickers and choose dates."),
                dcc.Link("Open", href="/hundred")
            ]),
            html.Div(className="card", children=[
                html.H3("Running the Risks"),
                html.P("Explore rolling volatility (risk). Adjust the window length."),
                dcc.Link("Open", href="/risks")
            ]),
        ]),
    ],
)
