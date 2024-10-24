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

app.layout = [
    html.Div(className='px-1 pt-2 my-2 text-center border-bottom', children=[
        html.H4(className="fw-bold text-body-emphasis", children='Bible Network'),
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
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks')
)
def update_verse(prev, next):
    print(f"updating verse...{NETWORK.get_fullname()} {prev} {next}")

    # did previous or next trigger?
    if prev is None and next is None:
        pass
    else :
        trigger = ctx.triggered_id
        NETWORK.previous_verse() if trigger == 'previous' else NETWORK.next_verse()

    # update verse and its associates
    verse = BUILDER.get_verse()
    crossrefs = BUILDER.get_crossrefs()
    graph = BUILDER.generate_graph()
    themes = BUILDER.get_themes()

    print(NETWORK.get_related_topics(k=30))
    
    return verse, crossrefs, graph, themes

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


        # if edge['target'] == node['data']['id']:
        #     stylesheet.append({
        #         "selector": 'node[id = "{}"]'.format(edge['source']),
        #         "style": {
        #             'background-color': follower_color,
        #             'opacity': 0.9,
        #             'z-index': 9999
        #         }
        #     })
            # stylesheet.append({
            #     "selector": 'edge[id= "{}"]'.format(edge['id']),
            #     "style": {
            #         "mid-target-arrow-color": follower_color,
            #         "mid-target-arrow-shape": "vee",
            #         "line-color": follower_color,
            #         'opacity': 1,
            #         'z-index': 5000
            #     }
            # })
    
    
# @callback(
#     Output("graph-tooltip", "show"),
#     Output("graph-tooltip", "bbox"),
#     Output("graph-tooltip", "children"),
#     Input("network", "mouseoverNodeData"),
#     Input("network", "elements"),
# )
# def display_hover(data, elements):
#     print(f"Hovering over... {data}")
#     if data is None:
#         return False, no_update, no_update

#     name = data['fullname']
#     verse = data['verse']
#     id = data['id']
#     # print(f"ELEMENTS {elements}")
#     # position = [elements][id]['position']
#     print(position)
#     bbox = {'x0': -1, 'x1': -1, 'y0': -1, 'y1': -1}

#     children = [
#         html.Div([
#             # html.H2(f"{desc}"),
#             html.P(f"{name}"),
#             # html.P(f"{desc}"),
#         ], style={'width': '200px', 'white-space': 'normal'})
#     ]

#     return True, bbox, children

# @callback(Output('network', 'children'),
#         Input('network', 'selectedNodeData'))
# def displaySelectedNodeData(data_list):
#     if data_list is None:
#         print("No data selected.")

#     labels = [data['label'] for data in data_list]
#     print(labels)
#     stylesheet = [{
#             "selector": 'node',
#             'style': {
#                 'opacity': 0.3,
#                 'shape': node_shape
#             }
#         }, {
#             'selector': 'edge',
#             'style': {
#                 'opacity': 0.2,
#                 "curve-style": "bezier",
#             }
#         }, {
#             "selector": 'node[id = "{}"]'.format(node['data']['id']),
#             "style": {
#                 'background-color': '#B10DC9',
#                 "border-color": "purple",
#                 "border-width": 2,
#                 "border-opacity": 1,
#                 "opacity": 1,

#                 "label": "data(label)",
#                 "color": "#B10DC9",
#                 "text-opacity": 1,
#                 "font-size": 12,
#                 'z-index': 9999
#             }
#         }]

#     for edge in node['edgesData']:
#         if edge['source'] == node['data']['id']:
#             stylesheet.append({
#                 "selector": 'node[id = "{}"]'.format(edge['target']),
#                 "style": {
#                     'background-color': following_color,
#                     'opacity': 0.9
#                 }
#             })
#             stylesheet.append({
#                 "selector": 'edge[id= "{}"]'.format(edge['id']),
#                 "style": {
#                     "mid-target-arrow-color": following_color,
#                     "mid-target-arrow-shape": "vee",
#                     "line-color": following_color,
#                     'opacity': 0.9,
#                     'z-index': 5000
#                 }
#             })

#         if edge['target'] == node['data']['id']:
#             stylesheet.append({
#                 "selector": 'node[id = "{}"]'.format(edge['source']),
#                 "style": {
#                     'background-color': follower_color,
#                     'opacity': 0.9,
#                     'z-index': 9999
#                 }
#             })
#             stylesheet.append({
#                 "selector": 'edge[id= "{}"]'.format(edge['id']),
#                 "style": {
#                     "mid-target-arrow-color": follower_color,
#                     "mid-target-arrow-shape": "vee",
#                     "line-color": follower_color,
#                     'opacity': 1,
#                     'z-index': 5000
#                 }
#             })

#     return stylesheet

# @callback(
#     Output('hover-data', 'children'),
#     Input('graph', 'hoverData'))
# def display_hover_data(hoverData):
#     print(hoverData)
#     #return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run(debug=True)