from dash import Dash, html, dcc, callback, ctx, Output, Input, no_update
import networkx as nx
import pandas as pd
import BibleNetwork as bn
import DashController as dc
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = [{
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm',
        'crossorigin': 'anonymous'
    }]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
NETWORK = bn.BibleNetwork()
STYLESHEET = dc.StyleSheet()
BUILDER = dc.DashController(NETWORK, STYLESHEET)
cyto.load_extra_layouts()

def get_inputs():
    BUILDER = dc.DashController(NETWORK, STYLESHEET)
    return BUILDER.get_inputs()

app.layout = [
    dcc.Store(id='id-store', data=''),
    html.Div(className='px-1 pt-2 my-2 text-center border-bottom', children=[
        html.H4(className="fw-bold text-body-emphasis", children='Bible Network'),
        html.Div(id='inputs', children=[BUILDER.get_inputs()]),
        html.Div(className='col-10 col-sm-8 col-lg-6 mx-auto', children=[
                    html.Div(className='d-grid gap-2 d-sm-flex justify-content-sm-center mb-5', style={'color': 'light-blue'}, children=[
                        html.Button(type='button', value='previous', id='previous', className='btn btn-primary px-4 me-sm-3', children='Previous'),
                        html.Button(type='button', value='next', id='next', className='btn btn-outline-secondary px-4 me-sm-3', children='Next'),
                    ]),
                    html.Div(id="graph", children=[]),
                    html.Div(id='main-verse', className='mb-4', children='lorem ipsum'),
                 ]),
    ]),
    html.Div(className='mx-3', children=[
        # dcc.Graph(id='graph-content'),
        html.Div(className='row', children=[
            html.Div(className='pt-1 col-6 sm-col-1', style={'min-width': '250px'}, children=[
                html.H6(children="Selected Verse"),
                html.Div(id='betweens', children=[html.P(children="lorem ipsum")]),
                html.H6(children="Cross References"),
                html.Div(id='crossrefs', children=[html.P(children="lorem ipsum")]),
            ]),
            html.Div(className='pt-1 col-6 sm-col-1', style={'min-width': '250px'}, children=[
                html.H6(children="Themes"),
                dcc.Tabs(id='themes', children=[html.P(children="lorem ipsum")], style={'display': 'inline-block', 'max-width': '500px'})
            ]),
        ])
    ])
]


### CALLBACKS ###
#################

@callback(
    Output('main-verse', 'children'),
    Output('crossrefs', 'children'),
    Output('graph', 'children'),
    Output('themes', 'children'),
    Output('id-store', 'data'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks'),
    Input('search', 'value'),
    Input('id-store', 'data')
)
def update_verse(prev, next, search, id):
    # initialise
    trigger = ctx.triggered_id
    id = NETWORK.get_random_id() if id == '' else id
    current_id = id

    print(f"updating verse...{NETWORK.get_fullname(id)} {prev} {next}")
    # did previous or next trigger?
    if prev is None and next is None:
        pass
    elif trigger == 'previous' or trigger == 'next' :
        id = id - 1 if trigger == 'previous' else id + 1
        # print(NETWORK.get_related_topics(k=30))

    if trigger == 'search':
        print(search)
        id = BUILDER.get_id_by_search(search, id)

    # update verse and its associates
    verse = BUILDER.get_verse(id)
    crossrefs = BUILDER.get_crossrefs(id)
    graph = BUILDER.generate_graph(id)
    themes = BUILDER.get_themes(id)

    return verse, crossrefs, graph, themes, id

@callback(
    Output('betweens', 'children'),
    Output('network', 'stylesheet'),
    Output('network', 'tapNode'),
    Input('network', 'tapNode'),
    Input('graph', 'n_clicks'),
    Input('themes', 'value'),
)
def update_styles(nodeData, clicked, theme):  
    default_stylesheet = STYLESHEET.get_default()
    trigger = ctx.triggered_id

    # is selected?
    if nodeData is not None:
        data = nodeData['data']
        stylesheet = STYLESHEET.highlight_paths(data['id'], data['path'])
        return BUILDER.get_betweens(data), stylesheet, None
    
    if trigger == 'themes':
        # Highlight themes
        stylesheet = select_theme(theme)
    else:
        stylesheet = STYLESHEET.get_default()
    
    return "No verse selected.", stylesheet, None

def select_theme(theme):
    # initialise data
    # theme = 'kingdom of god'
    key = f"theme.{theme}"
    # key = f"theme.jesus"
    # key = f"fullname ^= 'Matt'"
    x = ''
    operator = ''
    selector = STYLESHEET._selector(x, key, operator=operator)
    stylesheet = STYLESHEET.get_default()
    stylesheet.extend(STYLESHEET.get_highlights(selector))
    return stylesheet

if __name__ == '__main__':
    app.run(debug=True)