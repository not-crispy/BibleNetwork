
from dash import Dash, html, dcc, callback, ctx, Output, Input, no_update, exceptions
import dash_bootstrap_components as dbc

COLOURS = {
    'default': '#000000',
    'highlight': '#41A3D6',
    'secondary': '#B3B3B3',

    'white': 'white',
    'black': '#000000',
    'dark blue': '#226B97',
    'blue': '#41A3D6',
    'grey blue': '#6cbccc',
    # 'old-blue': '#4183D9', 
    'dark grey': "#3B3B3B",
    'mid grey': '#808080',
    'grey': '#999999',
    'light grey': '#B3B3B3',
    'footer': 'rgba(65,163,214,1)', # === blue
}

class DashBuilder():
    """Utilities to build the View using Html and Bootstrap components."""

    def get_em(self, children, id=""):
        return html.Em(children=children, id=id)

    def get_p(self, children, id=""):
        return html.P(children=children, id=id)       
    
    def get_span(self, children, id=""):
        return html.Span(children=children, id=id)

    def get_a(self, children, href="", id=""):
        return html.A(children=children, id=id, href=href)

    def get_link(self, children, href="", id="", classes=""):
        return dcc.Link(children, href=href, id=id, className=classes)

    def get_input(self, id="", type="", placeholder="", classes=""):
        return dcc.Input(id=id, type=type, placeholder=placeholder, className=f"{classes} btn")
    
    def get_button(self, id="", children="", fancy=False, basic=False, classes='', styles={}):
        classes = f'fancy-button light-border {classes}' if fancy else classes
        classes = f'basic-button light-border {classes}' if basic else classes
        return html.Button(id=id, value=id, type='button', style=styles, className=f"{classes} btn", children=children)
  
    def get_newsletter_button(self, styles={}, classes=""):
        return self.get_button(basic=True, styles=styles, classes=classes, children=self.get_emphasis('#Receive news & updates in your inbox.#', italics=False))

    def get_div(self, children, id="", classes=""):
        return html.Div(children=children, id=id, className=classes)

    def get_header(self):
        header = html.Div(id='header', children=[
            self.get_link(html.Img(src=r"/assets/logo.png", className="logo"), href="/")
            ])
        return header

    def get_hero_box(self, children, id=''):
        box = html.Div(className="border-box text-center mx-auto", children=children, id=id)
        return box

    def get_content_box(self, children, id='', focus=False, center=True, classes='', full_width=False):
        focus = 'focus' if focus else ''
        center = 'text-center' if center else ''
        size_wrapper = '' if full_width else 'box-wrapper'
        box_content = 'py-4' if full_width else 'box-content'

        box = html.Div(className=f"{center} {size_wrapper} {classes}", 
                    children=html.Div(children, className=f"{focus} mx-auto {box_content}"), 
                    id=id)
        return box

    def get_emphasis(self, text, delimiter="#", italics=True, emphasise_all=False):
        text = [text] if emphasise_all else text.split(delimiter)
        new_text = []

        # Decode text and emphasis any text that is between delimiters
        for phrase in text:
            i = text.index(phrase) + 1
            if i % 2 == 1: # odd index
                new_text.append(phrase)
            else: # even index
                classes = "emphasis" if italics else "emphasis no-italics"
                new_text.append(html.Span(phrase, className=classes))

        return new_text

    def get_text(self, text, delimiter="#", size='h1', id='', classes='', color='default', hero=True):
        """Return a div containing the hero text. Any text surrounded by # is emphasised.
        e.g. text='This is #Bible Network#""" 

        text = self.get_emphasis(text)
        size = size.lower()

        if size == 'h1':
            x = html.H1
        elif size == 'h2':
            x = html.H2
        elif size == 'h3':
            x = html.H3
        elif size == 'h4':
            x = html.H4
        elif size == 'h5':
            x = html.H5
        elif size == 'h6':
            x = html.H6
        elif size == 'p':
            x = html.P
        elif size == 'span':
            x = html.Span

        # Get colour
        if color in COLOURS:
            color = COLOURS[color]
        else:
            color = COLOURS['default']

        # Get classes
        classes = "text mx-auto "+classes
        classes = "hero "+classes if hero else classes
        container = x(className=classes, children=text, id=id, style={'color': color})
        return container

    def get_row(self, content=[], classes=""):
        container = html.Div(className="container "+classes, children=[
            html.Div(className="row", children=content)
        ])
        return container
    
    def get_slide(self, start_index, items, visible=4):
        """Build the wrapper for a carousel slide."""
        
        visible_items = items[start_index:start_index + visible]
        if len(visible_items) < visible:
            visible_items += items[:visible - len(visible_items)]

        return dbc.Row([
                dbc.Col(
                    self.get_div(
                        self.get_div([
                                self.get_text(it["name"], size='h4', classes="emphasis"),
                                self.get_text(it["verse"], size='p', classes="fancy", hero=False),
                                html.A("Explore now \u2192", href=it['link'], className="emphasis arrow"),
                            ], classes="px-2"),
                        classes="h-100 px-2 py-3 shadow-sm carousel-card",
                    ),
                    md=3, sm=6, xs=12, className="position-relative px-0 mb-4"
                )
                for it in visible_items
            ],
            className="g-3 justify-content-center",
        )
        
    def get_carousel(self):
        """Build the skeleton for an interactive carousel."""
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.Button("\u276E", id="prev-btn", n_clicks=0, className="btn btn-outline-primary"),
                    width="auto",
                    align="center",
                ),
                dbc.Col(id="carousel-content", width=True),
                dbc.Col(
                    html.Button("\u276F", id="next-btn", n_clicks=0, className="btn btn-outline-primary"),
                    width="auto",
                    align="center",
                    ),
                ],
                className="align-items-center text-center mt-4",
                ),
            ],
            fluid=True,
        )