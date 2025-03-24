from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

def init_dash(url_path: str, app) -> Dash:
    # Initialize Dash app
    dash_app = Dash(server=app, url_base_pathname=url_path)
    
    # Get DataFrame from config
    df = app.config.get("df").copy()
    df['-log10(adj.P.Val)'] = -np.log10(df['adj.P.Val'])
    
    # Dash layout
    dash_app.layout = html.Div([
        html.A("⬅ Back to Main Page", href="/", className="back-button"),
        html.H1("Volcano Plot", className="title"),

        # Centered container for controls and graph
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("Figure Width:", className="input-label"),
                        dcc.Input(id="fig-width", type="number", value=1200, min=400, max=1600, step=100, className="styled-input"),
                    ], className="input-group"),

                    html.Div([
                        html.Label("Figure Height:", className="input-label"),
                        dcc.Input(id="fig-height", type="number", value=700, min=300, max=1200, step=100, className="styled-input"),
                    ], className="input-group"),
                ], className="input-container"),

                dcc.Slider(
                    id='significance-slider',
                    min=0.01,
                    max=0.1,
                    value=0.05,
                    marks=None,
                    tooltip={"placement": "bottom"}
                ),
            ], className="controls"),

            # Graph container
            html.Div([
                dcc.Graph(id='volcano-plot')
            ], className="graph-container")
        ], className="centered-container")
    ], className="page-container")

    @dash_app.callback(
        Output('volcano-plot', 'figure'),
        [Input('significance-slider', 'value'),
         Input('fig-width', 'value'),
         Input('fig-height', 'value')]
    )
    def update_plot(significance_level, fig_width, fig_height):
        df['Significance'] = df['adj.P.Val'] < significance_level
        df['Color'] = df.apply(lambda row: 'red' if row['Significance'] and row['logFC'] > 0 
                               else ('blue' if row['Significance'] else 'gray'), axis=1)
        
        fig = px.scatter(
            df,
            x="logFC",
            y="-log10(adj.P.Val)",
            color="Color",
            hover_name="EntrezGeneSymbol",
            title="Volcano Plot",
            labels={
                "logFC": "Log2 Fold Change",
                "-log10(adj.P.Val)": "-log10 Adjusted P-Value"
            },
            color_discrete_map={"red": "red", "blue": "blue", "gray": "gray"}
        )
        
        # Apply user-defined figure size
        fig.update_layout(
            width=fig_width,
            height=fig_height
        )
        
        return fig
    
    return dash_app.server
