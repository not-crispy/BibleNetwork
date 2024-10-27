from dash import Dash, html, dcc, callback, ctx, Output, Input, no_update
import networkx as nx
import pandas as pd
import BibleNetwork as bn
import dash_cytoscape as cyto
import json
import re

class StyleSheet():
    """Utility to build stylesheets"""
    def __init__(self):
        self.label = 'data(label)'
        self.label_size = 12
        self.colours = {
            'default': 'grey',
            'active': '#BFD7B5', # green
            'hl1': '#B10DC9', # mauve
            'hl2': 'purple',
            'focus': 'green',
            'buttons': 'grey',

        }
        self.default = self._create_default()

    def get_default(self):
        return self._create_default()
    
    def get_base(self, id):
        return self._create_base(id)
       
    def get_highlights(self, selector):
        styles = [
            {
                "selector": selector,
                "style": {
                    'background-color': self.colours['focus'],
                    'line-color': self.colours['focus'],
                    'opacity': 0.9,
                    'z-index': 9999
                }
            }]
        return styles
       
    def highlight_paths(self, id, paths):
        stylesheet = self.get_base(id)
        
        max_edges = len(paths) - 1
        index = 0
        for id in paths:
            # Set node colour
            selector = self._node_selector(id, 'id')
            stylesheet.extend(self.get_highlights(selector))

            # Are there any edges left?
            index += 1
            if index > max_edges: 
                break 

            # Set edge colour
            edge_id = f"{id}-{paths[index]}"
            selector = self._edge_selector(edge_id, 'id')
            stylesheet.extend(self.get_highlights(selector))

        return stylesheet
    
    def get_tabs(self):
        defaults = {
            'padding': '6px',
            'fontWeight': '400',
            'width': 'fit-content',
            'min-width': '100px',
            'margin': '3px',
            'borderBottom': '1px solid #d6d6d6',
            'borderTop': '1px solid #d6d6d6',          
        }
        tab_style = {
            'background-color': self.colours['buttons'],
            'background-image': 'none',
            'border-color': self.colours['buttons'],
            'color': 'white',
        }
        tab_selected_style = {
            'color': 'black',
            'fontWeight': '500',
            'padding': '6px',
            'margin': '3px',
            'width': 'fit-content',
            'color': self.colours['buttons'],
            'background-color': 'transparent',
            'background-image': 'none',
            'border-color': self.colours['buttons'],
        }
        return tab_style | defaults, tab_selected_style | defaults
    
    def _selector(self, x, key='id', element='node', operator='='):
        """ Build a custom stylesheet selector.

        default: node[id = "{search}"] -- select node with id 'x' """
        if x == '':
            selector = f"{element}[{key} {operator}]"
        else:
            selector = f"{element}[{key} {operator} '{x}']"
        # print(f"Generated selector... {selector}")
        return selector
    
    def _node_selector(self, x, key='id'):
        """ Build a stylesheet selector for nodes."""
        return self._selector(x, key=key, element='node')
        
    def _edge_selector(self, x, key='id'):
        """ Build a stylesheet selector for edges."""
        return self._selector(x, key=key, element='edge')
    
    def _create_default(self):
        styles = [
            {
                'selector': 'node',
                'style': {
                    'background-color': self.colours['default'],
                    'label': self.label,
                    'font-size': self.label_size
                }
            },
            {
                'selector': 'node[active="active"]',
                'style': {
                    'background-color': self.colours['active'],
                }
            },]
        return styles
    
    def _create_base(self, id):
        styles = [{
            "selector": 'node',
            'style': {
                'opacity': 0.3,
                # 'shape': node_shape
            }
        }, {
            'selector': 'edge',
            'style': {
                'opacity': 0.2,
                # "curve-style": "bezier",
            }
        }, {
            "selector": f'node[id = "{id}"]',
            "style": {
                'background-color': self.colours['hl1'],
                "border-color": self.colours['hl2'],
                "border-width": 2,
                "border-opacity": 1,
                "opacity": 1,

                "label": self.label,
                "color": self.colours['hl1'],
                "text-opacity": 1,
                "font-size": self.label_size,
                'z-index': 100
            }
        }]
        return styles

    
class DashController():
    """Utilities to build the View using the Model (i.e. BibleNetwork)."""
    def __init__(self, network, stylesheet):
        self.network = network
        self.styles = stylesheet
        self.default_stylesheet = self.styles.get_default()

    def get_em(self, children, id=""):
        return html.Em(children=children) if id == "" else html.Em(children=children, id=id)
    
    def get_div(self, children, id=""):
        return html.Div(children=children) if id == "" else html.Div(children=children, id=id)

    def get_p(self, children, id=""):
        return html.P(children=children) if id == "" else html.P(children=children, id=id)        

    def get_verse(self, id):
        """Returns verse as a div."""
        name = self.get_em(self.network.get_fullname(id))
        verse = self.get_p(self.network.get_verse(id))
        return self.get_div([name, verse])
    
    def get_themes(self, id):
        """Returns themes as a list of tabs."""
        tabs = []
        tab_style, selected_style = self.styles.get_tabs()
        # print(self.network.get_related_topics())
        for theme, weight in self.network.get_related_topics(id).items():
            tab = dcc.Tab(label=theme, value=self.network.sanitise(theme), className='btn btn-outline-info', 
                          style=tab_style, selected_style=selected_style)
            tabs.append(tab)

        return tabs
    
    def get_dropdown(self, items, id=""):
        """Returns a dropdown of verses."""
        options = []
        for item in items:
            options.append(item)

        dropdown = dcc.Dropdown(
            options,
            id=id
        )

        return dropdown
    
    def get_troubleshoots(self):
        inputs = html.Div([
            html.Span(["cross-refs:"]),
            dcc.Input(id=f"crossrefs-troubleshoot", type='number', placeholder=5),
            html.Span(["factor:"]),  
            dcc.Input(id=f"factor-troubleshoot", type='number', placeholder=0.35),
            ])
        
        return inputs
    
    def get_inputs(self):
        msg = "type a verse... eg. Matthew 4:3"
        inputs = html.Div([  
            dcc.Input(id=f"search", type='text', placeholder=f"{msg}")
            ])
        
        return inputs
    
    def get_taxonomy(self):
        path = "bible.json"
        with open(path, 'r') as config_file:
            bible_taxonomy = json.load(config_file)
        return bible_taxonomy
    
    def get_verses_dropdown(self):
        """Returns a book / chapter / verse dropdown."""

        bible = self.get_taxonomy()        
        books = bible.keys()
        # chapters = 
        book_drop = self.get_dropdown(books)
        
    def get_betweens(self, nodeData):
        """Returns verses between the selected points as a list of divs."""
        children = []
        count = 1
        max = 1

        # get verse and create it
        for id in reversed(nodeData['path']):
            children.append(self.get_verse(id))
            
            # max reached ?
            count = count + 1 if count < max else -1 
            if count == -1 : break 

        return children
    
    def get_crossrefs(self, source_id):
        """Returns crossrefs as a list of divs."""
        children = []
        count = 1
        max = 5    
        for crossref in self.network.get_crossrefs(source_id):
            # build crossreferences
            id = crossref[0]
            children.append(self.get_verse(id))

            # don't get more than max cross references
            count = count + 1 if count < max else -1 
            if count == -1 : break 

        return children
    
    def generate_edges(self, G):
        edges = [
            {'data': {'source': str(source), 'target': str(target), 'id': f"{source}-{target}"}}
            for source, target, data in G.edges(data=True)
        ]
        return edges
    
    def generate_nodes(self, G, active_id):
        # initialise
        network = self.network
        factor = 200
         
         # build nodes
        nodes = [
            {
                'data': {'id': str(id), 'label': data['name'], 'fullname': network.get_fullname(id), 'verse': data['content'], 'path': data['path'],
                        'active': 'active' if id == active_id else 'inactive', 'theme': network.get_topics(id)
                        }, 
                'selectable': True,
                'fit': False,
                # 'position': {'x': (data['position'][0]) * factor, 'y': (data['position'][1]) * factor},

            }
            for id, data in ( G.nodes(data=True) )
        ]

        # print(f"A sample node... {G.nodes(data=True)}")
        return nodes
    
    def get_prev_next(self, id):
        return {id - 1, id, id + 1}
        
    def generate_fig(self, id, factor, cutoff, styles=""):     
        # build nodes and edges
        active_id = id
        # id = self.get_prev_next(id)
        
        # G = self.network.get_related_subgraph(factor=factor, id=id)
        G = self.network.get_related_subgraph_force_crossrefs(factor=factor, id=id, how_many=cutoff)
        G = self.network.get_best_related_subgraph(id=id)
        nodes = self.generate_nodes(G, active_id)
        edges = self.generate_edges(G)
        styles = self.default_stylesheet if styles == "" else styles

        # build figure
        fig = cyto.Cytoscape(
            id='network',
            layout={
                    'name': 'cose-bilkent',
                    'animate': True,
                    # 'zoom': 10,
                    # 'fit': False,
                    },
            elements=edges+nodes,
            stylesheet=styles,
            style={'width': '100%', 'height': '450px'},
            zoom=1,
            maxZoom=1.4,
            minZoom=0.4,
            wheelSensitivity=0.1,
        )
        return fig
        
    def decode_search(self, search):
        search = search.strip()
        search = re.sub(r'[^(\.\w :)]', '', search) # delete specials
        search = re.sub(r'[ ]+', ' ', search) # remove double spaces
        search = search.replace(':', '.').replace(' ', '.')
        search = search.split('.', 3)
        print(search)

        if len(search) < 3 :
            return ""
        
        if search[0] in ['1', '2', '3'] :
            num, bk, ch, vs = search[:4]
            bk = bk.capitalize()
            bk = f"{num} {bk}"
        else :
            bk, ch, vs = search[:3]
            bk = bk.capitalize()

        taxonomy = self.get_taxonomy()
        bk = self.get_book_by_search(bk, taxonomy)
        print(bk, ch, vs)

        
        if bk == "": 
            return ""
        
        return f"{bk}.{ch}.{vs}"

    def get_book_by_search(self, search, taxonomy):
        for book, items in taxonomy.items():
            if search in items['spellings']:
                return taxonomy[book]['short']        

    def get_id_by_search(self, search, current_id=""):
        id = self.decode_search(search)
        id = self.lookup_id(id) if id != "" else "" # only do if a reference is given
        id = current_id if id == "" else id
        return id
    
    def lookup_id(self, verse):
        """Lookup the id of a verse based on a given reference e.g. Matt.3.3"""
        # Initialise verse lookup 
        print(f"looking up! {verse}")
        path = "verse_lookup.json"
        with open(path, 'r') as config_file:
            lookup = json.load(config_file)

        # Conduct lookup and return ID
        id = lookup[verse] if verse in lookup else ""
        return id

    def generate_graph(self, id):
        return [self.generate_fig(id=id), dcc.Tooltip(id="graph-tooltip")]
    
    def generate_graph(self, id, cutoff, factor):
        print(cutoff, factor)
        return [self.generate_fig(id=id, cutoff=cutoff, factor=factor), dcc.Tooltip(id="graph-tooltip")]


if __name__ == '__main__':
    network = bn.BibleNetwork()
    stylesheet = StyleSheet()
    controller = DashController(network, stylesheet)
    searches = ["afhasdsadas", "^3k&dx", 'Matthew 1.4', 'Genesis 2:6', 'gen 15:15', 'Genesis 23:10', 'Ecclesssia 4.11', '&&&Matthew 21:10', 'Matt 04:3']
    for search in searches:
        print(f"search: {search} result: {controller.get_id_by_search(search)}")
    # print(controller.build_div([32,4,5]))