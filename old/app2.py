from dash import Dash, html, Input, Output, callback
import dash_cytoscape as cyto
import BibleNetwork as bn

app = Dash(__name__)
NETWORK = bn.BibleNetwork()

default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)'
        }
    }
]

def generate_graph(styles=default_stylesheet):
    G, degree = NETWORK.get_related_verses(1)
    nodes = generate_nodes(G)
    edges = generate_edges(G)
    fig = cyto.Cytoscape(
        id='graph',
        layout={'name': 'cose'},
        elements=edges+nodes,
        stylesheet=default_stylesheet,
        style={'width': '100%', 'height': '450px'}
    )

    return fig

def generate_nodes(G):
    nodes = [
        {'data': {'id': str(id), 'label': data['name'], 'fullname': NETWORK.get_fullname(id), 'verse': data['content']}}
        for id, data in G.nodes(data=True)
    ]
    return nodes

def generate_edges(G):
    edges = [
        {'data': {'source': str(source), 'target': str(target)}}
        for source, target, data in G.edges(data=True)
    ]
    return edges

app.layout = html.Div([
    generate_graph(),
    html.P(id='cytoscape-tapNodeData-output'),
    html.P(id='cytoscape-tapEdgeData-output'),
    html.P(id='cytoscape-mouseoverNodeData-output'),
    html.P(id='cytoscape-mouseoverEdgeData-output')
])

# @callback(Output('cytoscape-tapNodeData-output', 'children'),
#               Input('graph', 'tapNodeData'))
# def displayTapNodeData(data):
#     if data:
#         return "You recently clicked/tapped the city: " + data['label']


# @callback(Output('cytoscape-tapEdgeData-output', 'children'),
#               Input('graph', 'tapEdgeData'))
# def displayTapEdgeData(data):
#     if data:
#         return "You recently clicked/tapped the edge between " + \
#                data['source'].upper() + " and " + data['target'].upper()


# @callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
#               Input('graph', 'mouseoverNodeData'))
# def displayTapNodeData(data):
#     if data:
#         return "You recently hovered over the city: " + data['label']


# @callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
#               Input('graph', 'mouseoverEdgeData'))
# def displayTapEdgeData(data):
#     if data:
#         return "You recently hovered over the edge between " + \
#                data['source'].upper() + " and " + data['target'].upper()


if __name__ == '__main__':
    app.run(debug=True)