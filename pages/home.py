from dash import Dash, html, dcc, callback, register_page, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_builder import DashBuilder
import BibleNetwork as bn
import DashController as dc
import dash_cytoscape as cyto

db = DashBuilder()

STYLESHEET = dc.StyleSheet()
BUILDER = dc.DashController(None, STYLESHEET)
cyto.load_extra_layouts()

content = [
    db.get_hero_box(id='home', children=[
                                db.get_text("The Bible is full of #connections#", size='h1'),
                                html.Img(src=r"/assets/network.png", className="twist position-absolute center-absolute", 
                                         style={'max-width': '85%', 'width': '615px'}),
                                BUILDER.get_search(classes="search", msg="Search a verse...", id="main-search")]),
    db.get_content_box([
        html.A([
            db.get_text("A cosmic, interconnected story.", size='h2', color='highlight'),], href="genesis/1-1"
            ),
        db.get_text(size='p', color='secondary',
                    text='An interactive tool that visualises all the cross-references in the Bible and shows how each verse is connected.')
        ], focus=True),
    db.get_content_box([
        db.get_text("How does a verse ‘fit in’ with the rest of the Bible?", size='h3', color='highlight', classes="box-wrapper"),
        db.get_carousel(),
        dcc.Store(id="carousel-index", data=0),
    ], center=True, full_width=True),    
]
home = content

register_page("index", path='/', layout=home)
register_page("home", path='/home', layout=home)