from dash import Dash, html, dcc, callback, page_registry, register_page, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import BibleNetwork as bn
import DashController as dc
import dash_cytoscape as cyto

print("NETWORK.py")
NETWORK = bn.BibleNetwork()
STYLESHEET = dc.StyleSheet()
BUILDER = dc.DashController(NETWORK, STYLESHEET)
cyto.load_extra_layouts()

lower = dc.get_network_lower()
popup = [dc.get_popup(id="info-box")]

network = lower

register_page("network", path_template='/<book>/<chapter>-<verse>', layout=network)

@callback(
        Output('id-store', 'data'),
        Output('id-store2', 'data'),
        Output('search', 'value'),
        Output('url', 'pathname'),
        Output('main-verse', 'children'),
        Output('graph', 'children'),
        Input('search', 'value'),
        Input('url', 'pathname'),
)
def set_ids(search, url):
    trigger = ctx.triggered_id
    page = dc.get_page_name(url, page_registry)
    print(f"Your trigger: {trigger} Your url is: {url} Your search is: {search} Your page is {page}")
    id1, id2 = BUILDER.get_id_by_url(url, page=page)

    if trigger == 'search' and search != None:
        print(f"searching for... {search}")
        id1 = BUILDER.get_id_by_search(search, id1)
    #elif search2:
    #     print(f"searching for... {search}")
    #     id1 = BUILDER.get_id_by_search(search, id)
    elif trigger == 'url':
        search = ''
    
    id1 = NETWORK.get_random_id() if id1 == '' else id1
    print(f"id1 = {id1} id2 = {id2} url = {url} search = {search}")
    url = BUILDER.get_url(id1, id2, page, url)
    print(f"new url {url}")
    verse = BUILDER.get_topheading(id1)
    graph = BUILDER.generate_graph(id1, id2, height="65vh")

    if url == "/" :
        style = {'display': 'none'}
    else:
        style = {}

    return id1, id2, search, url, verse, graph


@callback(
        Output('crossrefs', 'children'),
        Output('themes', 'children'),
        Output('crossref-title', 'children'),
        Input('id-store', 'data'),
        Input('id-store2', 'data'),
)
def set_crossrefs(id1, id2):
    crossrefs = BUILDER.get_crossrefs(id1)
    themes = BUILDER.get_themes(id1)
    crossref_title = BUILDER.get_crossrefs_title(id1)
    return crossrefs, themes, crossref_title

@callback(
        Output('inputs', 'children'),
        Input('inputs', 'children')
)
def get_inputs(troubleshoot=False):
    BUILDER = dc.DashController(NETWORK, STYLESHEET)
    search = BUILDER.get_search()
    troubleshoots = BUILDER.get_troubleshoots
    return [search, troubleshoots] if troubleshoot else [search]


#### WORKS FOR MULTIPLE IDS ####

# @callback(
#     Output('main-verse', 'children'),
#     Output('crossrefs', 'children'),
#     Output('graph', 'children'),
#     Output('themes', 'children'),
#     Input('id-store', 'data'),
#     Input('id-store2', 'data'),
#     Input("breakpoints", "widthBreakpoint"),
# )
# def get_graph(id1, id2, bp):
#     # update verse and its associates
#     print(f"id1: {id1} id2: {id2}")
#     verse = BUILDER.get_topheading(id1)
#     crossrefs = BUILDER.get_crossrefs(id1)
#     graph = BUILDER.generate_graph(id1, id2, height="65vh")
#     themes = BUILDER.get_themes(id1)

#     return verse, crossrefs, graph, themes

#### ONLY WORKS FOR A SINGLE ID ####
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
#         id = BUILDER.get_id_by_url(url)[0]

#     id = NETWORK.get_random_id() if id == '' else id

#     print(id)

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
    # Input('info-box-wrapper', 'n_clicks'),
    Input('main-wrapper', 'n_clicks'),
    State("breakpoints", "width"),
    # Make main wrapper z-index == 10 when info box is open ... this will solve it
)
def update_styles(nodeData, clicked, theme, clicked2, window_width):  
    default_stylesheet = STYLESHEET.get_default()
    trigger = ctx.triggered_id

    print("clicked")

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
