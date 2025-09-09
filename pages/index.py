from dash import dcc, register_page
from flask import session

register_page(__name__, path="/")

def layout():
    # go to /home if logged in, else /login
    target = "/home" if session.get("user") else "/login"
    return dcc.Location(pathname=target, id="root-redirect")
