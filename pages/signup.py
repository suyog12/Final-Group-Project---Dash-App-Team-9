from dash import html, dcc, register_page, Input, Output, State, callback
from flask import session
from utils.auth_db import create_user, AuthError

register_page(__name__, path="/signup", name="Sign up")

layout = html.Div(
    id="signup-page",
    className="page auth-page",
    children=[
        dcc.Location(id="signup-redirect"),
        html.H2("Create an account"),
        html.Div(
            className="controls auth-form",
            children=[
                html.Div(className="control", children=[html.Label("Username"), dcc.Input(id="su-username", type="text")]),
                html.Div(
                    className="control",
                    children=[html.Label("Date of Birth"), dcc.DatePickerSingle(id="su-dob", display_format="MM-DD-YYYY")],
                ),
                html.Div(className="control", children=[html.Label("Password"), dcc.Input(id="su-pass1", type="password")]),
                html.Div(
                    className="control",
                    children=[html.Label("Confirm Password"), dcc.Input(id="su-pass2", type="password")],
                ),
                html.Div(className="auth-actions", children=[html.Button("Create account", id="su-btn", className="btn")]),
                html.Div(
                    className="auth-switch",
                    children=["Already have an account? ", dcc.Link("Sign in", href="/login", className="link-inline")],
                ),
            ],
        ),
        html.Div(id="signup-msg", className="auth-msg"),
    ],
)

@callback(
    Output("signup-msg", "children"),
    Output("signup-redirect", "pathname"),
    Input("su-btn", "n_clicks"),
    State("su-username", "value"),
    State("su-dob", "date"),
    State("su-pass1", "value"),
    State("su-pass2", "value"),
    prevent_initial_call=True,
)
def do_signup(n, username, dob, p1, p2):
    if not username or not dob or not p1 or not p2:
        return "All fields are required.", None
    if p1 != p2:
        return "Passwords do not match.", None
    try:
        create_user(username, p1, dob)
    except AuthError as e:
        return str(e), None
    session["user"] = (username or "").strip()
    return "Account created.", "/dashboard"
