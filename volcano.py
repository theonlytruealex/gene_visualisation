from dash import Dash, dcc, html, Input, Output, no_update
import plotly.express as px
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")
def init_dash(url_path: str, app) -> Dash:
    # Initialize Dash app
    dash_app = Dash(server=app, url_base_pathname=url_path)
    
    # Get DataFrame from config
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
                html.Label("Significance level", className="input-label"),
                dcc.Slider(
                    id='significance-slider',
                    min=0.01,
                    max=0.1,
                    value=0.05,
                    marks=None,
                    tooltip={"placement": "bottom"}
                ),
            ], className="controls"),

            # Graph container for volcano plot
            html.Div([
                dcc.Graph(id='volcano-plot', clickData=None)
            ], className="graph-container"),

            # Box plot container (initially hidden)
            html.Div(id="boxplot-container", style={"display": "none"}, children=[
                html.H2("Expression Data", className="boxplot-title"),
                dcc.Graph(id='box-plot')
            ])
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
            height=fig_height,
            showlegend=False
        )
        
        return fig

    @dash_app.callback(
        [Output('box-plot', 'figure'),
         Output('boxplot-container', 'style')],
        Input('volcano-plot', 'clickData')
    )
    def update_boxplot(clickData):
        if clickData is None:
            return no_update, {"display": "none"}  # Hide box plot if no point is clicked

        # Extract clicked gene
        clicked_gene = clickData['points'][0]['hovertext']  # Assumes hover_name="EntrezGeneSymbol"

        # Retrieve expression data (assuming df has expression data per sample)
        expression_data = app.config.get("expression_data")  # DataFrame where rows = genes, columns = samples
        if expression_data is None or clicked_gene not in expression_data.index:
            return px.box(title=f"No expression data found for {clicked_gene}"), {"display": "block"}

        # Convert expression data to long format for box plot
        df_long = expression_data.loc[clicked_gene].reset_index()
        df_long.columns = ["Sample", "Expression"]

        # Create box plot
        fig = px.box(df_long, y="Expression", title=f"Expression Distribution for {clicked_gene}")

        return fig, {"display": "block"}  # Show box plot after click

    return dash_app.server
