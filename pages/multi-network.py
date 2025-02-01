from dash import Dash, html, dcc, callback, register_page, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import BibleNetwork as bn
import DashController as dc
import dash_cytoscape as cyto

print("MULTI-NETWORK.py")
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
    page = dc.get_page_name("link")
    return page + divs

register_page("multi-network", path_template='/link/<book>/<chapter>-<verse>/<book>/<chapter>-<verse>', layout=layout())
register_page("multi-network", path_template='<book>/<chapter>-<verse>/<book>/<chapter>-<verse>', layout=layout())


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
