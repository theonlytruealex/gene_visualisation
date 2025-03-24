from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

def init_dash(url_path: str, app) -> Dash:
    # Initialize Dash app
    dash_app = Dash(server=app, url_base_pathname=url_path)
    
    # Get DataFrame from config
    df = app.config.get("df")
    
    # Create appropriate figure based on data availability
    if df is None:
        fig = px.scatter(title="Volcano Plot (Data Not Available)")
    elif not {'logFC', 'adj.P.Val', 'EntrezGeneSymbol'}.issubset(df.columns):
        fig = px.scatter(title="Volcano Plot (Required Columns Missing)")
    else:
        # Process data and create plot
        df['-log10(adj.P.Val)'] = -np.log10(df['adj.P.Val'])
        df['Significance'] = df['adj.P.Val'] < 0.05
        
        fig = px.scatter(
            df,
            x="logFC",
            y="-log10(adj.P.Val)",
            color="Significance",
            hover_name="EntrezGeneSymbol",
            title="Volcano Plot",
            labels={
                "logFC": "Log2 Fold Change",
                "-log10(adj.P.Val)": "-log10 Adjusted P-Value"
            },
            color_discrete_map={True: "red", False: "blue"}
        )
    
    # Set up layout
    dash_app.layout = html.Div(
        children=[
            html.A("⬅ Back to Main Page", href="/", className="back-button"),
            html.H1("Volcano Plot", className="title"),
            dcc.Graph(id='volcano-plot', figure=fig)
        ],
        className="container"
    )
    
    return dash_app.server
