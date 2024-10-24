from dash import Dash, html, dcc, callback, ctx, Output, Input
import networkx as nx
import plotly.express as px
import pandas as pd
import BibleNetwork as bn
import plotly.graph_objs as go

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = [{
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm',
        'crossorigin': 'anonymous'
    }]
app = Dash(__name__, external_stylesheets=external_stylesheets)
NETWORK = bn.BibleNetwork()

def trace_nodes(G, pos, degree):
    node_trace = go.Scatter(x=[], y=[], mode='markers', hoverinfo='text', hovertext=[],
        marker=dict(
        showscale=True,
        # colorscale='YlGnBu',
        colorscale='Viridis', 
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(thickness=15, title='Node Connections', xanchor='left', titleside='right'),  
        line=dict(width=2))
        )
    
    for node in G.nodes():
        x, y = pos[G.nodes[node]['id']]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([NETWORK.get_name(node)])
        node_trace['marker']['color'] += tuple([degree[node]]) # seperate colour by closeness to "starting" node

    return node_trace

def trace_edges(G, pos):
    edge_trace = go.Scatter(x=[], y=[],
    line=dict(width=0.5,color='#888'),
    hoverinfo='none',
    mode='lines')
    
    for edge in G.edges():
        x0, y0 = pos[G.nodes[edge[0]]['id']]
        x1, y1 = pos[G.nodes[edge[1]]['id']]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    return edge_trace

def generate_graph():
    print(NETWORK.get_id(), NETWORK.get_fullname())
    G, degree = NETWORK.get_related_verses(1)
    pos = nx.spring_layout(G)
    edge_trace = trace_edges(G, pos)
    node_trace = trace_nodes(G, pos, degree)
    
    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            # annotations=[ dict(
            #     showarrow=False,
            #     xref="paper", yref="paper",
            #     x=0.005, y=-0.002 ) ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    return fig

app.layout = [
    html.Div(className='px-1 pt-2 my-2 text-center border-bottom', children=[
        html.H4(className="fw-bold text-body-emphasis", children='Bible Network'),
        html.Div(className='col-10 col-sm-8 col-lg-6 mx-auto', children=[
                    html.Div(className='d-grid gap-2 d-sm-flex justify-content-sm-center mb-5', style={'color': 'light-blue'}, children=[
                        html.Button(type='button', value='previous', id='previous', className='btn btn-primary px-4 me-sm-3', children='Previous'),
                        html.Button(type='button', value='next', id='next', className='btn btn-outline-secondary px-4 me-sm-3', children='Next'),
                    ]),
                    html.Div(dcc.Graph(id='graph',figure=generate_graph(), hoverData={'points': [{'customdata': 'Japan'}]})),
                    html.Div(id='main-verse', className='mb-4', children='lorem ipsum'),
                 ]),
    ]),
    html.Div(className='mx-3', children=[
        # dcc.Graph(id='graph-content'),
        html.Div(className='row', children=[
            html.Div(className='pt-1 col-6 sm-col-1', style={'min-width': '250px'}, children=[
                html.H6(children="Cross References"),
                html.Div(id='crossrefs', children=[html.P(children="lorem ipsum")])
            ]),
            html.Div(className='pt-1 col-6 sm-col-1', style={'min-width': '250px'}, children=[
                html.H6(children="Themes"),
                html.Div(id='themes', children=[html.P(children="lorem ipsum")])
            ]),
        ])
    ])
]

@callback(
    Output('main-verse', 'children'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks')
)
def update_verse(b1, b2):
    # did previous or next trigger?
    print(f"updating verse...{NETWORK.get_fullname()}")
    trigger = ctx.triggered_id
    NETWORK.previous_verse() if trigger == 'previous' else NETWORK.next_verse()

    # update verse
    children = [html.Em(children=NETWORK.get_fullname()), 
                html.P(children=NETWORK.get_verse())]
    return children

@callback(
    Output('crossrefs', 'children'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks')
)
def update_crossref(b1, b2):
    crossrefs = NETWORK.get_crossrefs()
    children = []
    count = 1
    max = 5    
    for ref in crossrefs:
        # build html to contain crossreference data
        id = ref[0]
        name = html.Em(children=NETWORK.get_fullname(id))
        verse = html.P(children=f"{NETWORK.get_verse(id)}")
        div = html.Div(children=[name, verse])
        children.append(div)

        # don't get more than max cross references
        count = count + 1 if count < max else -1 
        if count == -1 : break 

    return children

@callback(
    Output('graph', 'figure'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks')
)
def update_graph(b1, b2):
    return generate_graph()

# @callback(
#     Output('hover-data', 'children'),
#     Input('graph', 'hoverData'))
# def display_hover_data(hoverData):
#     print(hoverData)
#     #return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run(debug=True)