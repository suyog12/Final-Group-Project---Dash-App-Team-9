from dash import dcc, register_page
from flask import session

register_page(__name__, path="/logout", name="Sign out")

def layout():
    session.pop("user", None)
    return dcc.Location(pathname="/login", id="logout-redirect")
