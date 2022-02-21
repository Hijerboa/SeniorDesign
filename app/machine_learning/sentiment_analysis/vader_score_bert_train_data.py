from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime

OUTPUT_FILE_PATH = 'app/machine_learning/sentiment_analysis/vader_scored_tweets.csv'
NUM_TWEETS = 30000

sia_obj = SentimentIntensityAnalyzer()


def vader_score(tweet_text: str):
    return sia_obj.polarity_scores(tweet_text) 


def generate_data():
    out_file = open(OUTPUT_FILE_PATH, 'w')

    initialize()
    session = create_session()
    tweets = session.query(Tweet).order_by(func.random()).limit(NUM_TWEETS).all()
    start = datetime.now()
    text = [t.text for t in tweets]
    for tweet in tweets:
        text = tweet.text.encode('utf-8').replace('\n', '').replace(',', '')
        score = vader_score(text)
        out_file.write(f'{score["compound"]},{text}\n')
    end = datetime.now()
    delta = end - start
    print(f'Took {delta.seconds} seconds')
