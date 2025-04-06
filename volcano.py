from dash import Dash, dcc, html, Input, Output, no_update
import plotly.express as px
import pandas as pd
import numpy as np
import requests

df = pd.read_csv("data.csv")
gene_info = pd.read_csv("values.csv")
donor_cols = [col for col in df.columns if '.OD' in col or '.YD' in col]

def init_dash(url_path: str, app) -> Dash:
    dash_app = Dash(server=app, url_base_pathname=url_path)

    df['-log10(adj.P.Val)'] = -np.log10(df['adj.P.Val'])
    dash_app.css.config.serve_locally = False

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.A("⬅ Back to Main Page", href="/", className="back-button")
            ], className="header-section"),

            html.H1("Volcano Plot", className="title"),

            html.Div([], className="spacer")  # empty right side to balance
        ], className="header-row"),


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

               html.Div([
                html.Label("Significance Level:", className="input-label"),
                dcc.Slider(
                    id='significance-slider',
                    min=0.01,
                    max=0.1,
                    value=0.05,
                    marks=None,
                    tooltip={"placement": "bottom"},
                    step=0.005,
                )
                ], className="input-group", style={"width": "300px"}),
            ], className="controls"),

            html.Div([
                dcc.Graph(id='volcano-plot', clickData=None)
            ], className="graph-container"),

            html.Div(id="boxplot-container", style={"display": "none", "max-width": "1200px"}, children=[
                html.Div([
                    dcc.Graph(id='box-plot', style={
                        "flex": "1",
                    }),

                    dcc.Loading(
                        id="loading-papers",
                        type="circle",
                        children=html.Div(id='pubmed-links', style={
                            "flex": "1",
                            "maxHeight": "400px",
                            "overflowY": "scroll",
                            "padding": "10px",
                            "border": "1px solid #ccc",
                            "borderRadius": "8px",
                            "max-width": "550px",
                            "margin-top": "40px"
                        })
                    )
                ], style={"display": "flex", "flexDirection": "row"}),

                dcc.Store(id="selected-gene")
            ])
        ], className="centered-container")
    ], className="page-container")

    # Volcano plot callback
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

        fig.update_layout(
            width=fig_width,
            height=fig_height,
            showlegend=False
        )
        return fig

    # Boxplot & gene store callback
    @dash_app.callback(
        [Output('box-plot', 'figure'),
         Output('boxplot-container', 'style'),
         Output('selected-gene', 'data')],
        Input('volcano-plot', 'clickData')
    )
    def update_boxplot(clickData):
        if clickData is None or 'points' not in clickData:
            return no_update, {"display": "none"}, no_update

        clicked_gene = clickData['points'][0].get('hovertext')
        if not clicked_gene:
            return no_update, {"display": "none"}, no_update

        gene_row = gene_info[gene_info['EntrezGeneSymbol'] == clicked_gene]
        donor_columns = [col for col in gene_info.columns if 'OD' in col or 'YD' in col]
        donor_values = gene_row[donor_columns]

        group = ['Old' if 'OD' in col else 'Young' for col in donor_columns]
        value = donor_values.values[0]

        plot_df = pd.DataFrame({'Group': group, 'Value': value})
        fig = px.box(plot_df, x='Group', y='Value', points='all',
                     title=f'Protein Concentration for {clicked_gene}')
        fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))

        return fig, {"display": "flex"}, clicked_gene

    # PubMed link callback
    @dash_app.callback(
        Output('pubmed-links', 'children'),
        Input('selected-gene', 'data')
    )
    def update_pubmed_links(gene_symbol):
        if not gene_symbol:
            return []

        try:
            gene_id = get_gene_id(gene_symbol)
            papers = get_pubmed_links(gene_id)
            links = [
                html.Div([
                    html.A(p['title'], href=p['url'], target="_blank",
                           style={"display": "block", "marginBottom": "10px"})
                ]) for p in papers
            ]
        except Exception:
            links = [html.Div("Failed to load PubMed articles.")]

        return links

    return dash_app.server

# --- API Utility Functions ---
def get_gene_id(gene_symbol):
    """Fetch MyGene.info gene ID from symbol (e.g., 'CDK2')."""
    url = f"https://mygene.info/v3/query?q=symbol:{gene_symbol}"
    response = requests.get(url).json()
    return response["hits"][0]["_id"]

def get_pubmed_links(gene_id):
    """Fetch PubMed titles/URLs for a gene ID."""
    url = f"https://mygene.info/v3/gene/{gene_id}?fields=generif"
    response = requests.get(url).json()
    pubmed_ids = response.get('generif', [])

    papers = []
    for pid in pubmed_ids:
        if 'text' in pid and 'pubmed' in pid:
            papers.append({
                "title": pid['text'],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid['pubmed']}"
            })
    return papers
