
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
    
    def get_button(self, id="", children="", fancy=False, classes='', styles={}):
        classes = f'fancy-button light-border {classes}' if fancy else classes #'btn btn-outline-secondary px-4 me-sm-3'
        return html.Button(id=id, value=id, type='button', style=styles, className=f"{classes} btn", children=children)
  
    def get_newsletter_button(self, styles={}):
        return self.get_button(fancy=True, styles=styles, children=[self.get_emphasis('#Receive news & updates in your inbox.#')])

    def get_div(self, children, id="", classes=""):
        return html.Div(children=children, id=id, className=classes)
        
    def get_footer(self):
        footer = html.Div(html.Div(id='footer', className="mx-auto", style={
            'background': f'linear-gradient({COLOURS['footer']}, rgba(0,0,0,0))'
        }, children=[
            # self.get_newsletter_button(styles={'float': 'right'}), ## TODO
            self.get_row([

            ]),
            self.get_div(classes='extra-rounded-borders mx-auto fancy-button light-border', 
                            children=self.get_text(size='h5', color='white', text='A #gospel-charged tool# for interactive exploration of cross-references, exegetical contexts, theology and themes.'))
        ]))
        return footer

    def get_header(self):
        header = html.Div(id='header', children=[
            self.get_link(html.Img(src=r"/assets/logo.png", className="logo"), href="/")
            ])
        return header

    def get_hero_box(self, children, id=''):
        box = html.Div(className="border-box text-center mx-auto", children=children, id=id)
        return box

    def get_content_box(self, children, id='', focus=False, center=True, classes=''):
        focus = 'focus' if focus else ''
        center = 'text-center' if center else ''
        box = html.Div(className=f"{center} box-wrapper {classes}", 
                    children=html.Div(children, className=f"{focus} mx-auto box-content"), 
                    id=id)
        return box

    def get_emphasis(self, text, delimiter="#"):
        text = text.split(delimiter)
        new_text = []

        # Decode text and emphasis any text that is between delimiters
        for phrase in text:
            i = text.index(phrase) + 1
            if i % 2 == 1: # odd index
                new_text.append(phrase)
            else: # even index
                new_text.append(html.Span(phrase))

        return new_text

    def get_text(self, text, delimiter="#", size='h1', id='', classes='', color='default'):
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
        elif size == 'p':
            x = html.P

        # Get colour
        if color in COLOURS:
            color = COLOURS[color]
        else:
            color = COLOURS['default']

        container = x(className="text hero mx-auto "+classes, children=text, id=id, style={'color': color})
        return container

    def get_row(self, content=[], classes=""):
        print(content)
        columns = [html.Div(className="col-sm", children=x) for x in content]

        container = html.Div(className="container "+classes, children=[
            html.Div(className="row", children=columns)
        ])
        return container