from dash import Dash, html, dcc, callback, register_page, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import BibleNetwork as bn
import DashController as dc
import dash_cytoscape as cyto

NETWORK = bn.BibleNetwork()
STYLESHEET = dc.StyleSheet()
BUILDER = dc.DashController(NETWORK, STYLESHEET)
cyto.load_extra_layouts()

divs = [html.Div(className='mx-3', children=[
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
    ]),]


def layout(**args):
    page = BUILDER.get_page_name("link")
    return page + divs

register_page("multi-network", path_template='/link/<book>/<chapter>-<verse>/<book>/<chapter>-<verse>', layout=layout())


@callback(
        Output('id-store', 'data'),
        Output('id-store2', 'data'),
        Output('search', 'value'),
        Output('url', 'pathname'),
        Input('search', 'value'),
        Input('url', 'pathname'),
        State('page_name', 'data')
)
def set_ids(search, url, page):
    trigger = ctx.triggered_id
    print(f"Your trigger: {trigger} Your url is: {url} Your search is: {search} Your page is {page}")
    id1, id2 = BUILDER.get_id_by_url(url, page=page)

    id1 = NETWORK.get_random_id() if id1 == '' else id1

    if trigger == 'search':
        print(f"searching for... {search}")
        id1 = BUILDER.get_id_by_search(search, id1)
    #elif search2:
    #     print(f"searching for... {search}")
    #     id1 = BUILDER.get_id_by_search(search, id)
    elif trigger == 'url':
        search = ''

    print(f"id1 = {id1} id2 = {id2} url = {url} search = {search}")
    url = BUILDER.get_url(id1, id2, page)
    return id1, id2, search, url

@callback(
    Output('main-verse', 'children'),
    Output('crossrefs', 'children'),
    Output('graph', 'children'),
    Output('themes', 'children'),
    Input('id-store', 'data'),
    Input('id-store2', 'data'),
    Input("breakpoints", "widthBreakpoint"),
)
def get_graph(id1, id2, bp):
    # update verse and its associates
    print(f"id1: {id1} id2: {id2}")
    verse = BUILDER.get_topheading(id1)
    crossrefs = BUILDER.get_crossrefs(id1)
    graph = BUILDER.generate_graph(id1, id2, height="65vh")
    themes = BUILDER.get_themes(id1)

    return verse, crossrefs, graph, themes

@callback(
    Input('network', 'mouseoverNodeData'),
)
def hover(nodeData):
    print(f"hover: {nodeData}")
    return
    
# dash.register_page(__name__, path_template='/<book>/<chapter>-<verse>')
# dash.register_page(__name__, path_template='/')

# def layout(book=None, chapter=None, verse=None, **kwargs):
#     print(f"printing... {book}, {chapter}, {verse}")
#     data = {'bk': book, 'ch': chapter, 'vs': verse}
#     # return dash.dcc.Location(id='url', data=data)
#     return 
#     return html.Div(
#         f"The user requested report ID: {book} {chapter} {verse}."
#     )
