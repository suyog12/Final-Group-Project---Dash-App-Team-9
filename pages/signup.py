from dash import html, dcc, register_page, Input, Output, State, callback
from flask import session
from utils.auth_db import create_user, AuthError

register_page(__name__, path="/signup", name="Sign up")

layout = html.Div(
    className="auth-shell",
    children=[
        dcc.Location(id="signup-redirect"),
        html.Div(
            className="auth-card",
            children=[
                html.H2("Create an account", className="auth-title"),
                html.P("Join in seconds. You’ll be redirected to your dashboard after sign-up.", className="auth-subtitle"),
                html.Div(id="signup-msg", className="auth-msg"),

                html.Div(
                    className="form-grid",
                    children=[
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Username", htmlFor="su-username"),
                                dcc.Input(
                                    id="su-username",
                                    type="text",
                                    placeholder="pick a username",
                                    className="form-input",
                                ),
                            ],
                        ),
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Date of Birth", htmlFor="su-dob"),
                                dcc.DatePickerSingle(
                                    id="su-dob",
                                    display_format="YYYY-MM-DD",
                                    className="date-input",
                                ),
                            ],
                        ),
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Password", htmlFor="su-pass1"),
                                dcc.Input(
                                    id="su-pass1",
                                    type="password",
                                    placeholder="••••••••",
                                    className="form-input",
                                ),
                            ],
                        ),
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Confirm Password", htmlFor="su-pass2"),
                                dcc.Input(
                                    id="su-pass2",
                                    type="password",
                                    placeholder="••••••••",
                                    className="form-input",
                                ),
                            ],
                        ),
                    ],
                ),

                html.Button("Create account", id="su-btn", className="auth-button"),
                html.Div(
                    className="auth-switch",
                    children=[
                        "Already have an account? ",
                        dcc.Link("Sign in", href="/login"),
                    ],
                ),
            ],
        ),
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
        return html.Div("All fields are required.", className="alert danger"), None
    if p1 != p2:
        return html.Div("Passwords do not match.", className="alert danger"), None

    try:
        create_user(username, p1, dob)
    except AuthError as e:
        return html.Div(str(e), className="alert danger"), None

    # auto-login on successful sign-up
    session["user"] = (username or "").strip()
    return html.Div("Account created!", className="alert success"), "/dashboard"
