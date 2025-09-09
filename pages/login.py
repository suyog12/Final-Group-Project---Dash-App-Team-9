from dash import html, dcc, register_page, Input, Output, State, callback
from flask import session
from utils.auth_db import verify_user

register_page(__name__, path="/login", name="Sign in")

layout = html.Div(id="login-page", children=[
    dcc.Location(id="login-loc"),
    dcc.Location(id="login-redirect"),
    html.H2("Sign in"),
    html.Div(className="controls", children=[
        html.Div(className="control", children=[
            html.Label("Username"),
            dcc.Input(id="login-username", type="text", placeholder="your username"),
        ]),
        html.Div(className="control", children=[
            html.Label("Password"),
            dcc.Input(id="login-pass", type="password", placeholder="••••••••"),
        ]),
        html.Button("Sign in", id="login-btn"),
        dcc.Link("Create an account", href="/signup")
    ]),
    html.Div(id="login-msg")
])

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
        return "Please enter username and password.", None
    if verify_user(username, pw):
        session["user"] = (username or "").strip()
        if search and "next=" in search:
            from urllib.parse import parse_qs
            target = parse_qs(search.lstrip("?")).get("next", ["/home"])[0]
            return "Signed in.", target
        return "Signed in.", "/home"
    return "Invalid credentials.", None
