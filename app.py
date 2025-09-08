from dash import Dash, html, dcc
import dash
import os
from dotenv import load_dotenv
load_dotenv()

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title="$100 Question")
server = app.server

app.layout = html.Div(id="site",
    children=[
        html.Header(id="site-header", children=[
            html.H1("The $100 Question"),
            html.P("What if you invested $100 in Apple and Microsoft? Explore growth and risk with simple, interactive charts."),
            html.Nav(id="site-nav", children=[
                dcc.Link("Home", href="/", className="nav-link"),
                dcc.Link("The $100 Question", href="/hundred", className="nav-link"),
                dcc.Link("Running the Risks", href="/risks", className="nav-link"),
            ]),
        ]),
        html.Main(id="site-main", children=[dash.page_container]),
        html.Footer(id="site-footer", children=[
            html.Small("Source: Alpha Vantage (TIME_SERIES_DAILY). Education-only; not investment advice.")
        ]),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
