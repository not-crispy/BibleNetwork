from dash import Dash, html, dcc, callback, ctx, Output, Input, no_update, exceptions
import networkx as nx
import pandas as pd
import BibleNetwork as bn
import dash_cytoscape as cyto
import json
import re

def get_page_name(name):
    return [dcc.Store(id='page_name', data=name)]
class StyleSheet():
    """Utility to build stylesheets"""
    def __init__(self):
        self.label = 'data(label)'
        self.label_size = 12
        self.colours = {
            'default': 'grey', #grey light
            'default-light': '#CFD2DB', #grey light
            'active': '#b4d3d9', # light blue
            'hl1': '#41A3D6', # blue
            'hl2': '#226B97', # dark blue
            'hl3': '#6cbccc', # grey blue
            'focus': '#226B97', # blue
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
                'selector': 'edge',
                'style': {
                    'line-color': self.colours['default'],
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
                'opacity': 0.3,
                'line-color': self.colours['default-light'],
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
                "color": self.colours['hl2'],
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
    
    def get_div(self, children, id="", className=""):
        return html.Div(children=children, id=id, className=className)

    def get_p(self, children, id=""):
        return html.P(children=children) if id == "" else html.P(children=children, id=id)        
    
    def get_span(self, children, id=""):
        return html.Span(children=children) if id == "" else html.Span(children=children, id=id)

    def get_a(self, children, href="", id=""):
        return html.A(children=children, href=href) if id == "" else html.A(children=children, href=href, id=id)  

    def get_link(self, children, href="", id=""):
        return dcc.Link(children, href=href, id=id)

    def get_input(self, id="", type="", placeholder=""):
        return dcc.Input(id=id, type=type, placeholder=placeholder, className="btn")

    def get_button(self, id="", children=""):
        classes = '' #'btn btn-outline-secondary px-4 me-sm-3'
        return html.Button(id=id, value=id, type='button', className=classes, children=children)      

    def get_verse(self, id, get_name=False):
        """Returns verse as a div."""
        name = self.get_em(self.network.get_fullname(id)) if get_name else ""
        verse = self.get_p(self.network.get_verse(id))
        return self.get_div([name, verse])
    
    def get_context(self, id):
        context = self.network.get_context(id)
        verses = []

        # Retreive passage. If active, place <span> tags around it
        for id in context['ids']:
            verse = self.network.get_verse(id)
            verse = self.get_span(verse, "context-active") if id == context['active'] else verse
            verses.append(verse)

        verses = self.get_p(verses)
        return verses
    
    def _get_url(self, id):
        """Converts verse into url in the form /bk/ch-vs"""
        data = self.network.get_dictname(id)
        return f"/{data['bk'].lower()}/{data['ch']}-{data['vs']}"
    
    def get_url(self, id1, id2="", page="default"):
        """For a given "page", gets the URL that corresponds to that page."""
        if page == "link":
           return f"/link{self._get_url(id1)}{self._get_url(id2)}"

        return self._get_url(id1)
    
    def get_topheading(self, id):
        # Get previous and next ids
        prev, x, next = self.get_prev_next(id=id)
        
        # Build buttons
        back = self.get_link(id="previous", children="◄", href=self.get_url(prev))
        forward = self.get_link(id="next", children="\u25BA", href=self.get_url(next))
        name = self.get_span([self.network.get_fullname(id)])
        name = self.get_div([back, name, forward], className='title')
        verses = self.get_verse(id)

        return self.get_div([name, verses])
    
    def get_passage(self, data):
        """Returns passage as a div."""
        name = self.get_em(data['name'])
        verse = self.get_p(data['passage'])
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
            self.get_input(id=f"crossrefs-troubleshoot", type='number', placeholder=5),
            html.Span(["factor:"]),  
            self.get_input(id=f"factor-troubleshoot", type='number', placeholder=0.35),
            ])
        
        return inputs
    
    def get_search(self):
        msg = "type a verse... eg. Matthew 4:3"
        inputs = html.Div([  
            self.get_input(id=f"search", type='text', placeholder=f"{msg}")
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
        path = nodeData['path']

        # get passage and create it
        for passage in reversed(self.network.get_path_passages(path)):
            children.append(self.get_passage(passage))
            
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
            children.append(self.get_verse(id, get_name=True))

            # don't get more than max cross references
            count = count + 1 if count < max else -1 
            if count == -1 : break 

        return children
    
    def get_column_left(self):
        """Returns the information for the left column for a page with a graph."""
        template = self.get_temp_selected_verse()+self.get_temp_crossrefs()
        c_left = [html.Div(className='pt-1 col-6 sm-col-1', style={'min-width': '250px'}, children=template),]
        return c_left
    
    def get_temp_crossrefs(self):
        """Returns the base template for crossrefs."""
        return [
           html.H6(children="Cross References"),
            html.Div(id='crossrefs', children=[html.P()]),
        ]
    
    def get_temp_selected_verse(self):
        """Returns the base template for selected verse."""
        return [
            html.H6(children="Selected Verse"),
            html.Div(id='betweens', children=[html.P()]),
        ]
    
    def get_temp_themes(self):
        """Returns the base template for themes."""
        return [
            html.H6(children="Themes"),
            dcc.Tabs(id='themes', children=[html.P()], style={'display': 'inline-block', 'max-width': '500px'}),
        ]
    
    def get_column_right(self):
        """Returns the information for the right column for a page with a graph."""
        template = self.get_temp_themes()
        c_right = [html.Div(className='pt-1 col-6 sm-col-1', style={'min-width': '250px'}, children=template)]
        return c_right    

    
    def get_lower(self):
        """Returns the lower information of a page with a graph."""
        lower = [html.Div(className='mx-3', children=[
            html.Div(className='row', children=self.get_column_left()+self.get_column_right())
        ]),]
        
        return lower
    
    def get_about(self):
        """Returns information about the project."""
        html.H6(children="Cross References"),
        html.Div(id='crossrefs', children=[html.P(children="lorem ipsum")]),
    
    def generate_edges(self, G):
        edges = [
            {'data': {'source': str(source), 'target': str(target), 'id': f"{source}-{target}"}}
            for source, target, data in G.edges(data=True)
        ]
        return edges
    
    def generate_nodes(self, G, active_ids):
        # initialise
        network = self.network
        factor = 200
         
         # build nodes
        nodes = [
            {
                'data': {'id': str(id), 'label': data['name'], 'fullname': network.get_fullname(id), 'verse': data['content'], 'path': data['path'],
                        'active': 'active' if id in active_ids else 'inactive', 'theme': network.get_topics(id)
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
        prev = self.network.previous_verse(id=id)
        next = self.network.next_verse(id=id)
        return [prev, id, next]
    
    def graph(self, id, id2=None, mode='default'):
        if id2 or id2 == 0:
            return self.network.get_path_related_subgraph(id1=id, id2=id2)
        
        return self.network.get_best_subgraph(id=id)
        
    def generate_fig(self, id, height, id2=None, styles=""):     
        # build nodes and edges
        active_ids = [id, id2]
        G = self.graph(id=id, id2=id2)
        nodes = self.generate_nodes(G, active_ids)
        edges = self.generate_edges(G)
        styles = self.default_stylesheet if styles == "" else styles

        # build figure
        fig = cyto.Cytoscape(
            id='network',
            layout={
                    'name': 'fcose',
                    'animate': True,
                    'animationDuration': 400,
                    'quality': 'proof',
                    # # 'zoom': 10,
                    'fit': True,
                    # 'padding': 30,
                    'idealEdgeLength': 40,
                    },
            elements=edges+nodes,
            stylesheet=styles,
            style={'width': '100%', 'height': height},
            zoom=1.1,
            zoomingEnabled=True,
            maxZoom=1.2,
            minZoom=0.4,
            wheelSensitivity=0.1,
            pan={'x': 0, 'y': 0},
            # responsive=True,
        )
    
        return fig
    
    def decode_search(self, search):
        search = search.strip()
        search = re.sub(r'[^(\.\w :)]', '', search) # delete specials
        search = re.sub(r'[ ]+', ' ', search) # remove double spaces
        search = search.replace(':', '.').replace(' ', '.')
        search = search.replace('1 ', '1').replace('2 ', '2').replace('3 ', '3') # parse 1 corinthians etc
        search = search.split('.', 3)
        print(f"search: {search}")

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
        
        if bk == "": 
            return ""
        
        return f"{bk}.{ch}.{vs}"

    def get_book_by_search(self, search, taxonomy):
        search = search.lower()
        for book, items in taxonomy.items():
            if search in items['spellings']:
                return taxonomy[book]['short']        

    def get_id_by_search(self, search, current_id=""):
        search = "" if search is None else search
        id = self.decode_search(search)
        id = self.network.get_id_by_name(id) if id != "" else "" # only do if a reference is given
        id = current_id if id == "" else id
        return id
    
    def _get_id_by_url(self, url):
        "input: genesis/1-2 ----> genesis 1.2"
        search = url.replace("/", " ").replace("-",".").strip()
        return self.get_id_by_search(search=search)
    
    def get_id_by_url(self, url, page="default"):
        "Parse the url based on the given page."
        id1, id2 = ["", ""]
        x = url.split("/")

        if page == "link":
            x = url.replace("/link", "").split("/")
            url1, url2 = [f"{x[1]}/{x[2]}", f"{x[3]}/{x[4]}"]
            id1 = self._get_id_by_url(url1)
            id2 = self._get_id_by_url(url2)
            print(f"items {url1}, {url2}, {id1}, {id2}")
            
        else:
            id1 = self._get_id_by_url(url)

        return [id1, id2]
    
    def generate_graph(self, id, id2=None, height="65vh"):
        if id2 or id2 == 0:
            print(f"generate! {id}, {id2}")
            return [self.generate_fig(id=id, id2=id2, height=height)]              
        
        return [self.generate_fig(id=id, height=height)]
    
    # Troubleshoot
    # def generate_graph(self, id, cutoff, factor):
    #     print(cutoff, factor)
    #     return [self.generate_fig(id=id, cutoff=cutoff, factor=factor), dcc.Tooltip(id="graph-tooltip")]

@callback(
    Output("url", "href"),
    Input("button", "n_clicks")
)
def test(n_click):
    if ctx.triggered_id == "button":
        return "/genesis/3-10"
    else:
        raise exceptions.PreventUpdate
    
if __name__ == '__main__':
    network = bn.BibleNetwork()
    stylesheet = StyleSheet()
    controller = DashController(network, stylesheet)
    searches = ["afhasdsadas", "^3k&dx", 'Matthew 1.4', 'Genesis 2:6', 'gen 15:15', 'Genesis 23:10', 'Ecclesssia 4.11', '&&&Matthew 21:10', 'Matt 04:3']
    for search in searches:
        print(f"search: {search} result: {controller.get_id_by_search(search)}")
    # print(controller.build_div([32,4,5]))