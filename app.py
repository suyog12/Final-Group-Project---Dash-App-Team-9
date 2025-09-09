import os
from dotenv import load_dotenv
load_dotenv()

from flask import session
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from utils.db import init_db

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title="$100 Question")
server = app.server
server.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# create tables if not present
try:
    init_db()
except Exception as e:
    print(f"[auth] DB init skipped: {e}")

def make_header():
    user = session.get("user")
    if user:
        nav = [
            dcc.Link("Company Name", href="/home", className="nav-link"),
            html.Span(style={"flex": "1"}),
            dcc.Link("The $100 Question", href="/hundred", className="nav-link"),
            dcc.Link("Running the Risks", href="/risks", className="nav-link"),
            html.Span(f"Signed in as {user}"),
            dcc.Link("Log out", href="/logout", className="nav-link"),
        ]
    else:
        nav = [
            dcc.Link("Login", href="/login", className="nav-link"),
            dcc.Link("Sign up", href="/signup", className="nav-link"),
        ]
    return html.Header(className="header", children=[
        #html.H1("The $100 Question"),
        #html.P("What if you invested $100 in Apple and Microsoft? Explore growth and risk with simple, interactive charts."),
        html.Nav(className="navbar", children=nav),
    ])

# session-aware layout
app.layout = lambda: html.Div(className="container", children=[
    make_header(),
    html.Div(className="page-container", children=[dash.page_container]),
    html.Footer(className="footer",
                children=html.Small("Source: Alpha Vantage (TIME_SERIES_DAILY). Education-only; not investment advice."))
])

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
