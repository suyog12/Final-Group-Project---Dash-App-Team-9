from dash import html, dcc, register_page, Input, Output, State, callback
from flask import session
from utils.auth_db import verify_user

register_page(__name__, path="/login", name="Sign in")

layout = html.Div(
    className="auth-shell",
    children=[
        dcc.Location(id="login-loc"),
        dcc.Location(id="login-redirect"),
        html.Div(
            className="auth-card",
            children=[
                html.H2("Sign in", className="auth-title"),
                html.P("Welcome back. Enter your details to access your dashboard.", className="auth-subtitle"),
                html.Div(id="login-msg", className="auth-msg"),

                html.Div(
                    className="form-grid one",
                    children=[
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Username", htmlFor="login-username"),
                                dcc.Input(
                                    id="login-username",
                                    type="text",
                                    placeholder="your username",
                                    className="form-input"
                                ),
                            ],
                        ),
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Password", htmlFor="login-pass"),
                                dcc.Input(
                                    id="login-pass",
                                    type="password",
                                    placeholder="••••••••",
                                    className="form-input"
                                ),
                            ],
                        ),
                    ],
                ),

                html.Button("Sign in", id="login-btn", className="auth-button"),
                html.Div(
                    className="auth-switch",
                    children=[
                        "Don't have an account? ",
                        dcc.Link("Create one", href="/signup"),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("login-msg", "children"),
    Output("login-redirect", "pathname"),
    Input("login-btn", "n_clicks"),
    State("login-username", "value"),
    State("login-pass", "value"),
    State("login-loc", "search"),
    prevent_initial_call=True,
)
def do_login(n, username, pw, search):
    if not username or not pw:
        return html.Div("Please enter username and password.", className="alert danger"), None

    if verify_user(username, pw):
        session["user"] = (username or "").strip()

        # respect next=? when present
        target = "/dashboard"
        if search and "next=" in search:
            from urllib.parse import parse_qs
            target = parse_qs(search.lstrip("?")).get("next", ["/dashboard"])[0]

        return None, target

    return html.Div("Invalid credentials. Please try again.", className="alert danger"), None
