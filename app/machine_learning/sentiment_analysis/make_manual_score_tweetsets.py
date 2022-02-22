from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime

IAN_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/ian.csv'
AIDAN_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/aidan.csv'
NICK_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/nick.csv'
NATHAN_FILE_PATH = 'app/machine_learning/sentiment_analysis/manual_tweet_sets/nathan.csv'
NUM_TWEETS = 1000


def make_manual_tweetsets():
    ian_file = open(IAN_FILE_PATH, 'w', encoding='utf-8', errors='replace')
    aidan_file = open(AIDAN_FILE_PATH, 'w', encoding='utf-8', errors='replace')
    nick_file = open(NICK_FILE_PATH, 'w', encoding='utf-8', errors='replace')
    nathan_file = open(NATHAN_FILE_PATH, 'w', encoding='utf-8', errors='replace')

    initialize()
    session = create_session()
    tweets = session.query(Tweet).order_by(func.random()).limit(NUM_TWEETS).all()
    print("GOT DEM TWEETS")
    for i in range(250):
        ian_file.write(tweets[i].text.replace('\n', '').replace(',', '') + '\n')
        aidan_file.write(tweets[i+250].text.replace('\n', '').replace(',', '') + '\n')
        nick_file.write(tweets[i+500].text.replace('\n', '').replace(',', '') + '\n')
        nathan_file.write(tweets[i+750].text.replace('\n', '').replace(',', '') + '\n')
