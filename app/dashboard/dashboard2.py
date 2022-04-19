from turtle import width
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
import json

from dash.dependencies import Input, Output, State
from db import database_connection as conn
from sqlalchemy.sql import func
import db.models as models

STYLE_BUTTON_CLOSED = 'fa bi-chevron-double-down mb-1'
STYLE_BUTTON_OPENED = 'bi bi-chevron-double-up mb-1'
LOREM_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

# Load these at startup for cheatsies
SLUGS = json.loads(open("./dashboard/manual_slugs.json").read())['slugs']
conn.initialize()
sess = conn.create_session()
BILLS = {bill.bill_id: bill for bill in sess.query(models.Bill).where(models.Bill.bill_id.in_(SLUGS)).all()}
sess.close()


# Somewhat cannibalized from the DBC documentation

def _getNavbar():  # TODO: Change icon to somehting else, add twitter links, remove search bar, make responsive dropdown open alternate search, make navbar toggler switch at proper screen size.
    LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
    
    dd_items = [{'label': BILLS[id].short_title[:70] + ('' if len(BILLS[id].short_title) < 70 else '...') , 'value': BILLS[id].bill_id} for id in BILLS.keys()]

    search_bar = dbc.Row(
        [
            dcc.Dropdown(id='bill-dropdown', options=dd_items, className='text-dark')
        ],
        className="g-0 ms-auto mt-3 mt-md-0 flex-fill",
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

# Get the sample sentiment chart display - PLACEHOLDER, NOT USED


def _getBillSentimentChart():
    df = px.data.iris()  # iris is a sample pandas DataFrame
    fig = px.scatter(df, x="sepal_width", y="sepal_length")

    parent_div = dcc.Graph(figure=fig, config={'autosizable': True})

    return parent_div

# Get the card for current bill information

# TODO: Make this into a parent class to be instantiated for different card/agg types.

# Card Template
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
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div(
                    html.I(className='fa-solid fa-face-laugh text-success p-3',
                           style={'font-size': "8rem"}),
                    className='d-flex justify-content-center'
                ),

                dbc.CardBody([
                    html.B('Sample Bill Text:'),
                    html.P(LOREM_TEXT)
                ], className='pt-0')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

#Card to display our sources
def _getAttributionsCard(i):
    #TODO: Add all of our sources in here
    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Our Sources',
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1 '), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                dbc.CardBody([
                    html.B('We would like to thank the following sources for allowing us to use their data for this project:'),
                    html.P(LOREM_TEXT)
                ], className='pt-0')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

#Card to display interaction weighted sentiment
def _getLogWeightedCard(i, bill_sent_logscaled):
    # Logic for determining what face/text to show:
    # TODO: Determine good/bad/neut from dict.
    sent_overall = 'Neutral'
    sent_color = 'text-warning '
    sent_icon = 'fa-face-meh '
    sent_header = 'Interaction Shows That This Bill is Neutral'
    sent_text = f'When accounting for how much interaction collected tweets recieved (Likes, Retweets, Replies), we found that the overall reaction to this bill was neutral with {bill_sent_logscaled["prop_positive"]:.2f}% of the weighted sentiments not leaning strongly in either direction.'

    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('When Accounting For Interaction, This Bill Is ' + sent_overall,
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1'), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div([
                    html.I(className='fa-solid p-3 ' + sent_icon +  sent_color,
                           style={'font-size': "8rem"}),
                    ],className='d-flex justify-content-center'
                ),

                dbc.CardBody([
                    html.H4(sent_header),
                    html.H5(sent_text)
                ], className='pt-0')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

#Card to display politician sentiment
def _getPoliticiansCard(i, bill_sent_politicians):
    # Logic for determining what face/text to show:
    # TODO: Determine good/bad/neut from dict.
    sent_overall = 'Bad'
    sent_color = 'text-danger '
    sent_icon = 'fa-face-laugh '
    sent_header = 'Politicians Aren\'t Happy About This Bill'
    sent_text = f'With {bill_sent_politicians["num_users"]:,} politicians tweeting about this bill, {bill_sent_politicians["prop_positive"]:.2f}% of their {bill_sent_politicians["count_total"]:,} tweets that passed our opinion threshold were found to view the bill negatively'

    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Bill Sentiment Among Politicians Is ' + sent_overall,
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1'), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div([
                    html.I(className='fa-solid p-3 fa-user-tie ' + sent_color,
                           style={'font-size': "8rem"}),
                    ],className='d-flex justify-content-center'
                ),

                dbc.CardBody([
                    html.H4(sent_header),
                    html.H5(sent_text)
                ], className='pt-0')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

#Card to display verified user sentiment
def _getVerifiedCard(i, bill_sent_verified):
    # Logic for determining what face/text to show:
    # TODO: Determine good/bad/neut from dict.
    sent_overall = 'Good'
    sent_color = 'text-success '
    sent_icon = 'fa-face-laugh '
    sent_header = 'Verified Users Like This Bill!'
    sent_text = f'With {bill_sent_verified["num_users"]:,} verified users tweeting about this bill, {bill_sent_verified["prop_positive"]:.2f}% of their {bill_sent_verified["count_total"]:,} tweets that passed our opinion threshold were found to view the bill favorably!'

    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Bill Sentiment Among Verified Users Is ' + sent_overall,
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1'), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div([
                    html.I(className='fa-solid p-3 fa-circle-check ' + sent_color,
                           style={'font-size': "8rem"}),
                    ],className='d-flex justify-content-center'
                ),

                dbc.CardBody([
                    html.H4(sent_header),
                    html.H5(sent_text)
                ], className='pt-0')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

#Card to display if bill has bipartisan support
def _getBipartisanCard(i, sponsor_counts):
    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('A Bipartisan Effort',
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1 '), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div([
                    dbc.CardBody([
                        html.H5(f'This bill has supporters from both sides of the aisle. {sponsor_counts["R"]} Republicans and {sponsor_counts["D"]} Democrats sponsored this bill!', className=''),
                    ], className=''),
                    html.Div(
                        html.I(className='fa-solid fa-handshake p-3 text-success',
                            style={'font-size': "4rem"}),
                        className='d-flex justify-content-center'
                    ),
                ], className='d-inline-flex align-items-center')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

#Card to display flat sentiment score
def _getFlatScalingCard(i, bill_sent_flat):
    # Logic for determining what face/text to show:
    # TODO: Determine good/bad/neut from dict.
    sent_overall = 'Good'
    sent_classes = 'fa-face-laugh text-success'
    sent_header = 'Overall reactions to this Bill have been positive!'
    sent_text = f'With {bill_sent_flat["num_users"]:,} users tweeting about this bill, {bill_sent_flat["prop_positive"]:.2f}% of the {bill_sent_flat["count_total"]:,} tweets collected that passed our opinion threshold were found to view the bill favorably!'

    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Unweighted Bill Sentiment Is ' + sent_overall,
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1'), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div(
                    html.I(className='fa-solid p-3 ' + sent_classes,
                           style={'font-size': "8rem"}),
                    className='d-flex justify-content-center'
                ),

                dbc.CardBody([
                    html.H4(sent_header),
                    html.H5(sent_text)
                ], className='pt-0')
            ], id='collapse-'+str(i), is_open=False)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

# Card to display if bill has a lot of actions associated with it
def _getHasManyActionsCard(i):
    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Hot Topic In Congress',
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1 '), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div([
                    dbc.CardBody([
                        html.H5('This bill has had more actions associated with it than most bills. Congress has been talking about this one quite a bit!', className=''),
                    ], className=''),
                    html.Div(
                        html.I(className='fa-solid fa-fire-flame-curved p-3 text-danger',
                            style={'font-size': "4rem"}),
                        className='d-flex justify-content-center'
                    ),

                ], className='d-inline-flex align-items-center')
            ], id='collapse-'+str(i), is_open=True,)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

# Card to display if bill is active
def _getIsActiveCard(i):
    parent_div = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4('Still Active',
                            className='text-align-center'),
                    html.Div(
                        html.I(id='button-collapse-'+str(i), className='bi bi-chevron-double-down mb-1 '), className='d-flex justify-content-end flex-fill')
                ], id='button-collapse-div-'+str(i), className='hstack w-100')
            ], className='bg-primary bg-opacity-25'),
            dbc.Collapse([
                html.Div([
                    html.Div(
                        html.I(className='fa-solid fa-arrow-right-arrow-left p-3',
                            style={'font-size': "4rem"}),
                        className='d-flex justify-content-center'
                    ),
                    dbc.CardBody([
                        html.H5('This Bill is still actively moving through Congress! Keep an eye out for changes in sentiment as the Bill progresses.', className=''),
                    ], className='')
                ], className='d-inline-flex align-items-center')
            ], id='collapse-'+str(i), is_open=True,)
        ], className='w-100')
    ], className='d-flex align-items-center h-75'
    )
    return parent_div

# TODO: Load data from the selected bill and populate relevant fields


def _getBillSummary(bill): 
    parent_div = html.Div(
        dbc.Card([
            dbc.CardHeader(html.H4('Bill Information'), className='bg-primary bg-opacity-25'),
            dbc.CardBody([
                html.H5(bill.title),
                html.B('BILL SUBJECT'),
                html.P(bill.primary_subject),
                html.B('BILL SPONSOR PARTY'),
                html.P('Democrat' if bill.sponsor_party == 'D' else 'Republican'),
                html.B('BILL SUMMARY'),
                html.P(bill.summary),
                html.B('BILL LINK'),
                html.Br(),
                html.A(bill.congressdotgov_url, href=bill.congressdotgov_url),
                html.P('...')
            ])
        ], className='h-100',
        ),
    )
    return parent_div

def _getInstructionCard(): #TODO: Fill this with usage instructions for page load
    parent_div = html.Div(
        dbc.Card([
            dbc.CardHeader(html.H4('Bill Summary'), className='bg-primary bg-opacity-25'),
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
        ], className='h-100',
        ),
    )
    return parent_div

def _getOffCanvas():  # TODO: Fill with bill search elements
    offcanvasSearchArea = html.Div([

    ])
    
    offcanvas = dbc.Offcanvas(
        offcanvasSearchArea,
        id="offcanvas",
        title="Title",
        is_open=False,
    )
    return offcanvas

# Server object for containerization


class Server:
    def __init__(self) -> None: #TODO: make header use favicon and set title accordingly

        # Load up our stylesheets
        # Get dash bootstrap CSS for normal components
        dbc_css = (
            "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
        )

        # Load styles for figures
        load_figure_template('vapor')
        # Create app context with stylesheets
        self.app = dash.Dash(__name__, external_stylesheets=[
                             dbc.themes.VAPOR, dbc.icons.BOOTSTRAP, "https://use.fontawesome.com/releases/v6.1.1/css/all.css", dbc_css],
                             meta_tags=[{'name':'viewport', 'content':'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}])

        # Build main app layout
        #searchArea = _makeSearchArea()
        self.app.layout = html.Div(children=[
            _getNavbar(),  # Get the navbar elements and place into the layout above the main container
            # Get the off canvas search area and place into the layout.
            #_getOffCanvas(searchArea),
            dbc.Container([
                dbc.Row([
                        dbc.Col(  # This column contains the bill information card
                            dbc.Container([
                                # placeholder for bill summary
                                dbc.Row(_getBillSummary(list(BILLS.values())[0]),
                                        className='h-100 pb-2 pt-2'),
                            ], id='bill-summary-container', className='mw-100 bill-info-div scroll-toggle'),
                            xl=6, lg=6, md=12, sm=12,),  # Set breakpoints for mobile responsiveness
                        dbc.Col(  # This column contains the sentiment info cards. #TODO: Load this from the bill result.
                            dbc.Container([
                                # placeholder for sentiment info
                                dbc.Row(_getAttributionsCard(1),
                                        className='pb-2 pt-lg-2'),
                                # placeholder for sentiment info
                                dbc.Row(_getIsActiveCard(2),
                                        className='pb-2'),
                                # placeholder for sentiment info
                                dbc.Row(_getHasManyActionsCard(3),
                                        className='pb-2'),
                                dbc.Row(_getFlatScalingCard(4, {'num_users': 6969, 'prop_positive': 69.6969, 'count_total': 420000}),
                                        className='pb-2'), 
                                dbc.Row(_getBipartisanCard(5, {'D': 4, 'R': 2}),
                                        className='pb-2'), 
                                dbc.Row(_getVerifiedCard(6, {'num_users': 420, 'prop_positive': 77.1234, 'count_total': 52560}),
                                        className='pb-2'), 
                                dbc.Row(_getPoliticiansCard(7, {'num_users': 30, 'prop_positive': 99.99, 'count_total': 10000}),
                                        className='pb-2'), 
                                dbc.Row(_getLogWeightedCard(8, {'num_users': 30, 'prop_positive': 65.00, 'count_total': 10000}),
                                        className='pb-2'),
                            ], id='info-card-container', className='mw-100 scroll-toggle'),
                            xl=6, lg=6, md=12, sm=12,),  # Set breakpoints for mobile responsiveness
                        ],),
            ],
                fluid=True,
            ),
            #dbc.Button([
            #    html.I(className='bi bi-chevron-double-right')
            #], id="open-offcanvas", n_clicks=0, className='offcanvas-toggle position-absolute translate-middle-vertical top-50 px-1'),
        ], className='min-vh-100 h-100'
        )

        # Register Card Collapses:
        # TODO this will be dynamic based on the number/type of cards added.
        for i in range(1, 99):
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
        self.app.run_server(debug=False, host='0.0.0.0')
