from dash import Dash, html, dcc, callback, page_registry, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash_breakpoints import WindowBreakpoints
from dash_builder import DashBuilder
# from dash_improve_my_llms import add_llms_routes
import pandas as pd
import DashController as dc
import BibleNetwork as bn

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
db = DashBuilder()

external_stylesheets = [{
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm',
        'crossorigin': 'anonymous'
    },
    {
        'href': 'https://fonts.googleapis.com/css2?family=Farro:wght@300;400;500;700&family=Hind+Mysuru:wght@300;400;500;600;700&family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=PT+Sans:ital,wght@0,400;0,700;1,400;1,700&display=swap',
        'rel': 'stylesheet',
    },
    {
        'href': "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        'rel': 'stylesheet',
    }]
app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
# add_llms_routes(app)

graph = dc.get_graph()

header = [
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='id-store', data=''),
    dcc.Store(id='id-store2', data=''),
    WindowBreakpoints(
            id="breakpoints",
            widthBreakpointThresholdsPx=[600, 1000, 1600],
            widthBreakpointNames=["sm", "md", "lg", "xl"],
        ),
    db.get_header(),
    # html.Div(id='header', className='py-2 fw-bold text-body-emphasis text-center border-bottom',children='Bible Network'),
]

app.layout = header + graph + [page_container] + [dc.get_footer()]

@callback(
        Output('graph-wrapper', 'style'),
        Input('url', 'pathname'),
)
def toggle_graph(url):
    if url == "/" :
        style = {'display': 'none'}
    else:
        style = {}

    return style

if __name__ == '__main__':
    app.run(debug=True)