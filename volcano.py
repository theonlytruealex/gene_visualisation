from dash import Dash, dcc, html, Input, Output, no_update
import plotly.express as px
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")
gene_info = pd.read_csv("values.csv")
donor_cols = [col for col in df.columns if '.OD' in col or '.YD' in col]

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
        if clickData is None or 'points' not in clickData:
            return no_update, {"display": "none"}


        clicked_gene = clickData['points'][0].get('hovertext') 
        if not clicked_gene:
            return no_update, {"display": "none"}

        gene_row = gene_info[gene_info['EntrezGeneSymbol'] == clicked_gene]

        donor_columns = [col for col in gene_info.columns if 'OD' in col or 'YD' in col]
        donor_values = gene_row[donor_columns]

        group = ['Old' if 'OD' in col else 'Young' for col in donor_columns]
        value = donor_values.values[0]

        plot_df = pd.DataFrame({
            'Group': group,
            'Value': value
        })

        fig = px.box(plot_df, x='Group', y='Value', points='all', title=f'Protein Concentration for {clicked_gene}')

        fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))

        return fig, {"display": "block"}


    return dash_app.server
