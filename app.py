from dash import Dash, html, dcc, callback, ctx, Output, State, Input, no_update, page_container, clientside_callback, ClientsideFunction
from dash_breakpoints import WindowBreakpoints
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = [{
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm',
        'crossorigin': 'anonymous'
    },
    {
        'href': 'https://fonts.googleapis.com/css2?family=Farro:wght@300;400;500;700&family=Hind+Mysuru:wght@300;400;500;600;700&family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=PT+Sans:ital,wght@0,400;0,700;1,400;1,700&display=swap',
        'rel': 'stylesheet',
    }]
app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

graph = [    
    html.Div(className='text-center border-bottom', children=[
        html.Div(className='col-sm-12 col-lg-10 col-md-12 col-xl-10 mx-auto', children=[
            html.Div(id="float-left", children=[
                html.Div(id='inputs'),
            ]),
            html.Div(id="float-right", children=[
                html.Div(children="a"),
            ]),
            html.Div(style={'min-width': '300px'}, children=[
                html.Div(id="graph"),
                html.Div(id='info-box-wrapper', className='absolute-centre', children=[html.Div(className='card', id='info-box')])
                ]),
            html.Div(id='main-verse', className='mb-4'), # sm-col-1 
            ]),
    ]),
    html.Div(className='d-grid gap-2 justify-content-sm-center mb-5', style={'display': 'none', 'color': 'light-blue'}, children=[ #d-sm-flex
        html.Button(type='button', value='previous', id='previous', className='btn btn-primary px-4 me-sm-3', children='Previous'),
        html.Button(type='button', value='next', id='next', className='btn btn-outline-secondary px-4 me-sm-3', children='Next'),
    ]),
]

header = [
    dcc.Location(id='url', refresh="callback-nav"),
    dcc.Store(id='id-store', data=''),
    dcc.Store(id='id-store2', data=''),
    WindowBreakpoints(
            id="breakpoints",
            widthBreakpointThresholdsPx=[600, 1000, 1600],
            widthBreakpointNames=["sm", "md", "lg", "xl"],
        ),
    html.Div(id='header', className='py-2 fw-bold text-body-emphasis text-center border-bottom',children='Bible Network'),
]

app.layout = header + graph + [page_container]

if __name__ == '__main__':
    app.run(debug=True)