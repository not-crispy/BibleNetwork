from dash import Dash, html, dcc, callback, register_page, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import BibleNetwork as bn
import DashController as dc
import dash_cytoscape as cyto

NETWORK = bn.BibleNetwork()
STYLESHEET = dc.StyleSheet()
BUILDER = dc.DashController(NETWORK, STYLESHEET)
cyto.load_extra_layouts()

lower = [html.Div(className='mx-3', children=[
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

page = BUILDER.get_page_name("default")

network = page + lower

register_page("index", path='/', layout=network)
register_page("network", path_template='/<book>/<chapter>-<verse>', layout=network)

@callback(
        Output('inputs', 'children'),
        Input('inputs', 'children')
)
def get_inputs(troubleshoot=False):
    BUILDER = dc.DashController(NETWORK, STYLESHEET)
    search = BUILDER.get_search()
    troubleshoots = BUILDER.get_troubleshoots
    return [search, troubleshoots] if troubleshoot else [search]


# @callback(
#     Output('main-verse', 'children'),
#     Output('crossrefs', 'children'),
#     Output('graph', 'children'),
#     Output('themes', 'children'),
#     Output('id-store', 'data'),
#     Output('url', 'pathname'),
#     Output('search', 'value'),
#     Input('search', 'value'),
#     Input('id-store', 'data'),
#     Input('url', 'pathname'),
#     Input("breakpoints", "widthBreakpoint"),
# )
# def update_verse(search, id, url, bp):

#     # initialise
#     trigger = ctx.triggered_id
#     print(f"Your trigger: {trigger} Your url is: {url} Your id is: {id}")

#     if url is not None:
#         id = BUILDER.get_id_by_url(url)

#     id = NETWORK.get_random_id() if id == '' else id

#     print(f"updating verse...{NETWORK.get_fullname(id)}")

#     if trigger == 'search':
#         print(f"searching for... {search}")
#         id = BUILDER.get_id_by_search(search, id)
#     elif trigger == 'url':
#         search = ''

#     # update verse and its associates
#     verse = BUILDER.get_topheading(id)
#     crossrefs = BUILDER.get_crossrefs(id)
#     graph = BUILDER.generate_graph(id)
#     themes = BUILDER.get_themes(id)
#     url = BUILDER.get_url(id)

#     return verse, crossrefs, graph, themes, id, url, search

@callback(
    Input('network', 'mouseoverNodeData'),
)
def hover(nodeData):
    print(f"hover: {nodeData}")
    return
    
@callback(
    Output('betweens', 'children'),
    Output('network', 'stylesheet'),
    Output('network', 'tapNode'),
    Output('info-box', 'children'),
    Output('info-box', 'style'),
    Input('network', 'tapNode'),
    Input('graph', 'n_clicks'),
    Input('themes', 'value'),
    State("breakpoints", "width"),
)
def update_styles(nodeData, clicked, theme, window_width):  
    default_stylesheet = STYLESHEET.get_default()
    trigger = ctx.triggered_id

    # is selected?
    if nodeData is not None:
        data = nodeData['data']
        x_pos, y_pos = (nodeData['position']['x'], nodeData['position']['y'])
        k = 0
        l = 300
        stylesheet = STYLESHEET.highlight_paths(data['id'], data['path'])

        print (f"y: {y_pos} direction: {k * (y_pos/abs(y_pos))} new_position: {y_pos + k * (y_pos/abs(y_pos))}")
        print (f"x: {x_pos} direction: {k * (x_pos/abs(x_pos))} new_position: {x_pos + k * (x_pos/abs(x_pos))}")
        print(f"window size: {window_width}")

        # Get bounds for #info-box

        max = 0.28 # the max-width of #info-box (i.e. 28vw)
        min = 250 # the min-width - 25px of #info-box (i.e. 225px)
        box_width = max * window_width if max * window_width > min else min
        bound_x = (window_width - box_width) / 2

        # Get x_pos for info-box      
        new_x = abs(x_pos) + 0.2 * window_width             # node position + approx 200px offset
        new_x = bound_x if new_x > bound_x else new_x
        new_x = new_x * (x_pos/abs(x_pos))

        info_styles = {
            'top': f'{y_pos + k * (y_pos/abs(y_pos))}px',  # Adjust this based on the node's y position
            'left': f'{x_pos + l * (x_pos/abs(x_pos))}px',  # Adjust this based on the node's x position
            'left': f'{new_x}px',
            # 'left': f'{x_pos + 0.2 * window_width * (x_pos/abs(x_pos))}px',

            'display': 'block',
        }

        betweens = BUILDER.get_betweens(data)

        return betweens, stylesheet, None, betweens, info_styles
    
    if trigger == 'themes':
        # Highlight themes
        stylesheet = select_theme(theme)
    else:
        stylesheet = STYLESHEET.get_default()
    
    return "No verse selected.", stylesheet, None, "", {'display': 'none'}

clientside_callback(
    ClientsideFunction(
        namespace='drag',
        function_name='draggable'
    ),
    Input('info-box', 'children')
)

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
