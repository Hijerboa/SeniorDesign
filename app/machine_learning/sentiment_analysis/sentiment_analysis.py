from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime


sia_obj = SentimentIntensityAnalyzer()

def vader_score(tweet_text: str):
    sentiment_dict = sia_obj.polarity_scores(tweet_text)
    return sentiment_dict


def bert_score(tweet_text: str):
    print()


def score_tweet(tweet_text: str):
    initialize()
    session = create_session()
    tweets = session.query(Tweet).limit(100).all()
    start = datetime.now()
    sentiments = [vader_score(t.text) for t in tweets]
    text = [t.text for t in tweets]
    end = datetime.now()
    delta = end - start
    for i in range(100):
        print(f'SCORE: {sentiments[i]}')
        print(f'TEXT: {text[i]}\n')
    print(f'Took {delta.seconds} seconds')

    # VADER score print
    # Bert score print
    return 0
