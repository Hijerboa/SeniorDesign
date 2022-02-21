import csv

from db.models import Tweet
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session


def dump_random_tweets():
    initialize()
    session = create_session()

    tweets = session.query(Tweet.text).order_by(func.random()).limit(100000).all()
    with open('random_tweets.csv', 'w') as file:
        csv_writer = csv.writer(file, delimiter=',')   
        for tweet in tweets:
            csv_writer.writerow([tweet[0], ''])

