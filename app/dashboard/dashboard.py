import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from db import database_connection as conn
from sqlalchemy.sql import func
import db.models as models

# Server object for containerization
class Server:
    def __init__(self) -> None:
        self.app = dash.Dash(__name__)

        # Start DB Connection
        conn.initialize()
        
        # Main Layout
        self.app.layout = html.Div(children=[
            html.H1(children='Bill Search.'),

            dcc.Dropdown(
                id="bill_search",
                options=[]
            ),

            html.Div(
                id="result_div",
                children='RESULT'
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

        @self.app.callback(
            Output("result_div", "children"),
            Input("bill_search", "value")
        )
        def find_and_report_sentiment(value):
            print(value)
            #Find tweets from bill and agg
            session = conn.create_session()
            print('Getting Phrases')
            bills = session.query(models.Bill).where(models.Bill.bill_id == value).all()
            if len(bills) == 0:
                return ''
            bill = bills[0]
            print('Phrases Returned')
            rsum = 0
            rcount = 0
            for phrase in bill.keywords:
                print(phrase.id)
                tweets = session.query(models.Tweet).where(models.Tweet.search_phrases.contains(phrase)).all()
                rcount += len(tweets)
                rsum += sum([t.sentiment for t in tweets])

            if rcount > 0:
                ravg = rsum / rcount
                return f'Done! Average sentiment is {ravg} over {rcount} tweets'
            else:
                return f'Done! No Tweets Found.'

    # Run this to start the server
    def run(self) -> None:
        self.app.run_server(debug=True)

