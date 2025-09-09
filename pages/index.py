from dash import dcc, register_page
from flask import session

register_page(__name__, path="/")

def layout():
    target = "/dashboard" if session.get("user") else "/home"
    return dcc.Location(pathname=target, id="root-redirect")
