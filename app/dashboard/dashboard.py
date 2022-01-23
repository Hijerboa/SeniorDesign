import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from db import database_connection as conn
import db.models as models
from dash.exceptions import PreventUpdate

# Server object for containerization
class Server:
    def __init__(self) -> None:
        self.app = dash.Dash(__name__)

        # Start DB Connection
        conn.initialize()
        
        # Main Layout
        self.app.layout = html.Div(children=[
            html.H1(children='Sentiment Dash-board'),

            html.H2(children='''
                Search By Bill:
            '''),

            dcc.Dropdown(
                id="bill_search",
                options=[]
            ),

            html.Div(
                id="bill_output",
                children=[]
            ),

            html.Div(
                id="tweet_output",
                children=[]
            )
        ])

        @self.app.callback(
            Output("bill_search", "options"),
            Input("bill_search", "search_value"),
        )
        def get_search_bills(search_value):
            if not search_value:
                raise PreventUpdate
            # Get the first 10 bills that match the given text
            session = conn.create_session()
            bills = session.query(models.Bill).where(models.Bill.title.ilike(f'%{search_value}%', escape='/')).limit(100).all()
            new_options = [{'label': bill.title, 'value': bill.bill_id} for bill in bills]
            session.close()
            return new_options

        @self.app.callback(
            Output("bill_output", "children"),
            Output("tweet_output", "children"),
            Input("bill_search", "value")
        )
        def populate_info(value):
            if not value:
                raise PreventUpdate
            # Get bill long info
            session = conn.create_session()
            bill, = session.query(models.Bill).where(models.Bill.bill_id == value).all()

            return [
                html.H2(children=bill.title),
                html.P(children=f'Last Action Date: {bill.latest_major_action_date}'),
                html.P(children=f'Last Action: {bill.latest_major_action}'),
                html.P(children=f'Summary: {bill.summary}')
            ], []

    # Run this to start the server
    def run(self) -> None:
        self.app.run_server(debug=True)

