from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime

IAN_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/ian2.csv'
AIDAN_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/aidan.csv'
NICK_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/nick.csv'
NATHAN_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/nathan.csv'
NUM_TWEETS = 500


def make_manual_tweetsets():
    ian_file = open(IAN_FILE_PATH, 'w', encoding='utf-8', errors='replace')

    initialize()
    session = create_session()
    tweets = session.query(Tweet).offset(10000).limit(NUM_TWEETS).all()
    print("GOT DEM TWEETS")
    for i in range(500):
        ian_file.write(tweets[i].text.replace('\n', '').replace(',', '') + '\n')
    session.close()
