from turtle import width
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash_bootstrap_templates import load_figure_template

from dash.dependencies import Input, Output, State
from db import database_connection as conn
from sqlalchemy.sql import func
import db.models as models

STYLE_BUTTON_CLOSED = 'fa bi-chevron-double-down mb-1 '
STYLE_BUTTON_OPENED = 'bi bi-chevron-double-up mb-1 '
LOREM_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

# Somewhat cannibalized from the DBC documentation


def _getNavbar(): # TODO: Change icon to somehting else, add twitter links, remove search bar, make responsive dropdown open alternate search.
    LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    # Bar for the search functionality. This will have a callback to update from the list of bills, etc.
    search_bar = dbc.Row(
        [
            dbc.Col(dbc.Input(type="search", placeholder="Search")),
            dbc.Col(
                dbc.Button(
                    "Search", color="primary", className="ms-2", n_clicks=0
                ),
                width="auto",
            ),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )

    # Overall navbar container
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Brand icon/link element
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=LOGO, height="30px")),
                            dbc.Col(dbc.NavbarBrand(
                                "INSERT SENIOR DESIGN TITLE", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                # Toggler for mobile responsiveness
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                # Collapse for mobile responsiveness
                dbc.Collapse(
                    search_bar,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
            fluid=True
        ),
        color="dark",
        dark=True,
        sticky='top',
        className='nav-class'
    )
    return navbar

# Get the sample sentiment chart display - PLACEHOLDER


def _getBillSentimentChart():
    df = px.data.iris()  # iris is a sample pandas DataFrame
    fig = px.scatter(df, x="sepal_width", y="sepal_length")

    parent_div = dcc.Graph(figure=fig, config={'autosizable': True})

    return parent_div

# Get the card for current bill information

#TODO: Make this into a parent class to be instantiated for different card/agg types.
def _getBillInfoCard(i):
    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Sample Bill Title For Info Card',
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1 '), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ]),
            dbc.Collapse([
                html.Div(
                    html.I(className='fa-solid fa-face-laugh text-success', style={'font-size':"8rem"}),
                    className='d-flex justify-content-center'
                ),

                dbc.CardBody([
                    html.B('Sample Bill Text:'),
                    html.P(LOREM_TEXT)
                ])
            ], id='collapse-'+str(i), is_open=False)
        ], color='dark', className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

# TODO: Load data from the selected bill
def _getBillSummary():
    parent_div = html.Div(
        dbc.Card([
            dbc.CardHeader(html.H4('Bill Summary')),
            dbc.CardBody([
                html.H5('Bill Title Here'),
                html.B('BILL SUMMARY'),
                html.P(LOREM_TEXT),
                html.B('BILL STATS'),
                html.Li('TEXT 1'),
                html.Li('TEXT 2'),
                html.Li('TEXT 3'),
                html.B('MORE BILL STUFF'),
                html.P(LOREM_TEXT),
                html.B('BILL LINK'),
                html.Br(),
                html.A('Bill/Link/url', href='/'),
                html.P('...')
            ])
        ], className='h-100', color='dark'
        ),
    )
    return parent_div


def _getOffCanvas(): #TODO: Fill with bill search elements
    offcanvas = dbc.Offcanvas(
            html.P(
                "This is the content of the Offcanvas. "
                "Close it by clicking on the close button, or "
                "the backdrop."
            ),
            id="offcanvas",
            title="Title",
            is_open=False,
        )
    return offcanvas

# Server object for containerization


class Server:
    def __init__(self) -> None:

        # Load up our stylesheets
        # Get dash bootstrap CSS for normal components
        dbc_css = (
            "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
        )

        # Load styles for figures
        load_figure_template('vapor')
        # Create app context with stylesheets
        self.app = dash.Dash(__name__, external_stylesheets=[
                             dbc.themes.VAPOR, dbc.icons.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css", dbc_css])

        # Build main app layout
        self.app.layout = html.Div(children=[
            _getNavbar(),  # Get the navbar elements and place into the layout above the main container
            _getOffCanvas(), #Get the off canvas search area and place into the layout.
            dbc.Container([
                dbc.Row([
                        dbc.Col(  # This column contains the bill information card
                            dbc.Container([
                                # placeholder for bill summary
                                dbc.Row(_getBillSummary(),
                                        className='h-100 pb-2 pt-2'),
                            ], className='mw-100 bill-info-div'),
                            xl=6, lg=6, md=12, sm=12,),  # Set breakpoints for mobile responsiveness
                        dbc.Col(  # This column contains the sentiment info cards.
                            dbc.Container([
                                # placeholder for sentiment info
                                dbc.Row(_getBillInfoCard(1),
                                        className='pb-2 pt-lg-2'),
                                # placeholder for sentiment info
                                dbc.Row(_getBillInfoCard(2),
                                        className='pb-2'),
                                # placeholder for sentiment info
                                dbc.Row(_getBillInfoCard(3),
                                        className='pb-2'),
                            ], className='mw-100 scroll-toggle'),
                            xl=6, lg=6, md=12, sm=12,),  # Set breakpoints for mobile responsiveness
                        ],),
            ],
                fluid=True,
            ),
            dbc.Button([
                html.I(className='bi bi-chevron-double-right')
            ], id="open-offcanvas", n_clicks=0, className='offcanvas-toggle position-absolute translate-middle-vertical top-50 px-1'),
        ], className='min-vh-100 h-100'
        )

        # Register Card Collapses:
        for i in range(1, 4): # TODO this will be dynamic based on the number/type of cards added.
            @self.app.callback(
                Output("collapse-"+str(i), "is_open"),
                Output("button-collapse-"+str(i), "className"),
                [Input("button-collapse-div-"+str(i), "n_clicks")],
                [State("collapse-"+str(i), "is_open")],
                [State("button-collapse-"+str(i), "className")]
            )
            def toggle_card_collapse(n, is_open, c_style):
                if n:
                    if is_open:
                        return not is_open, STYLE_BUTTON_CLOSED
                    else:
                        return not is_open, STYLE_BUTTON_OPENED
                return is_open, c_style

        # add callback for toggling navbar collapse on small screens
        @self.app.callback(
            Output("navbar-collapse", "is_open"),
            [Input("navbar-toggler", "n_clicks")],
            [State("navbar-collapse", "is_open")],
        )
        def toggle_navbar_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # add callback for opening the offcanvas
        @self.app.callback(
            Output("offcanvas", "is_open"),
            Input("open-offcanvas", "n_clicks"),
            [State("offcanvas", "is_open")],
        )
        def toggle_offcanvas(n1, is_open):
            if n1:
                return not is_open
            return is_open

    # Run this to start the server
    def run(self) -> None:
        self.app.run_server(debug=True)
