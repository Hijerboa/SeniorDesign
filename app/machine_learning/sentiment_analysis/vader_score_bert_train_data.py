from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime

OUTPUT_FILE_PATH = 'app/machine_learning/sentiment_analysis/new_100000'
NUM_TWEETS = 1000000

sia_obj = SentimentIntensityAnalyzer()


def vader_score(tweet_text: str):
    return sia_obj.polarity_scores(tweet_text) 


def generate_data():
    initialize()
    session = create_session()
    tweets = session.query(Tweet).order_by(func.random()).limit(NUM_TWEETS).all()

    for i in range(0, 10):
        out_file = open(f'{OUTPUT_FILE_PATH}_{i}.csv', 'w', encoding='utf-8', errors='replace')
        start = datetime.now()
        start_index = i*100000
        end_index = ((i+1) * 100000) - 1
        for tweet in tweets[start_index: end_index]:
            text = tweet.text.replace('\n', '').replace(',', '')
            score = vader_score(text)
            out_file.write(f'{score["compound"]},{text}\n')
        end = datetime.now()
        delta = end - start
        print(f'Took {delta.seconds} seconds')
