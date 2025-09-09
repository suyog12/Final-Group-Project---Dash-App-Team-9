import os
from dotenv import load_dotenv
load_dotenv()

from flask import session
from dash import Dash, html, dcc
import dash

from utils.db import init_db

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title="The $100 Question")
server = app.server
server.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# init DB tables (safe if exist)
try:
    init_db()
except Exception as e:
    print(f"[auth] DB init skipped: {e}")

def header():
    user = session.get("user")

    # Logo (acts as home before login, dashboard after login)
    home_target = "/dashboard" if user else "/home"
    logo = dcc.Link(
        html.Img(
            src="/assets/images/company-logo.svg",
            className="logo",
            alt="Company logo"
        ),
        href=home_target,
        className="logo-link"
    )

    # Left nav (only when authenticated)
    nav_items = []
    if user:
        nav_items = [
            dcc.Link("Dashboard", href="/dashboard", className="nav-link"),
            dcc.Link("The $100 Question", href="/hundred", className="nav-link"),
            dcc.Link("Daily Trading Activity", href="/activity", className="nav-link"),
            dcc.Link("Volatility", href="/volatility", className="nav-link"),
        ]

    # Right side: profile menu (authed) or auth buttons (anon)
    if user:
        right = html.Details(
            className="profile-menu",
            children=[
                html.Summary(
                    html.Img(src="/assets/images/profile-avatar.jpg",
                             alt="Profile", className="avatar"),
                    className="profile-summary"
                ),
                html.Div(
                    className="profile-dropdown",
                    children=[
                        html.Div(f"Signed in as {user}", className="profile-muted"),
                        dcc.Link("Log out", href="/logout", className="menu-item"),
                    ]
                ),
            ]
        )
    else:
        right = html.Div(
            className="auth-buttons",
            children=[
                dcc.Link("Login", href="/login", className="btn"),
                dcc.Link("Sign up", href="/signup", className="btn"),
            ]
        )

    return html.Header(
        className="header",
        children=[
            logo,
            html.Nav(className="navbar", children=nav_items),
            right,
        ],
    )

# Session-aware layout
app.layout = lambda: html.Div(
    className="container",
    children=[
        header(),
        html.Div(className="page-container", children=[dash.page_container]),
        html.Footer(
            className="footer",
            children=html.Small(
                "Source: Alpha Vantage (TIME_SERIES_DAILY). Education-only; not investment advice."
            ),
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
