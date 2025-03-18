from dash import dcc, html, Dash
from flask import g
def init_dash(url_path, app):
    dash_app = Dash(server=app, url_base_pathname=url_path)

    dash_app.layout = html.Div(children=[
        html.A(id="logout-link", children="Main page", href="/"),
        html.H1("Welcome to my Dash App", style={"textAlign": "center"}),
        html.Div(id="dummy"),
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Category 1'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Category 2'},
                ],
                'layout': {'title': 'Dash Data Visualization'}
            }
        ),
    ])


    return dash_app.server