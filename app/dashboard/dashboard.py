import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from db import database_connection as conn
import db.models as models

# Server object for containerization
class Server:
    def __init__(self) -> None:
        self.app = dash.Dash(__name__)

        # Start DB Connection
        conn.initialize()
        
        # Main Layout
        self.app.layout = html.Div(children=[
            html.H1(children='Hello, Dash.'),

            html.Div(children='''
                Test Filler Text.
            '''),

            dcc.Dropdown(
                id="bill_search",
                options=[]
            )
        ])

        @self.app.callback(
            Output("bill_search", "options"),
            Input("bill_search", "search_value")
        )
        def get_search_bills(search_value):
            # Get the first 10 bills that match the given text
            session = conn.create_session()
            bills = session.query(models.Bill).where(models.Bill.short_title.ilike(f'%{search_value}%', escape='/')).limit(10).all()
            options = [{'label': bill.title, 'value': bill.bill_id} for bill in bills]
            session.close()
            return options

    # Run this to start the server
    def run(self) -> None:
        self.app.run_server(debug=True)

