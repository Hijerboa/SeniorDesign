from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime

sia_obj = SentimentIntensityAnalyzer()
def score(document):
    sentiment_dict = sia_obj.polarity_scores(document)
    #print('--------------------------------------------------')
    #print(document)
    #print()
    #print(f'+: {sentiment_dict["pos"]}| -: {sentiment_dict["neg"]}| o: {sentiment_dict["neu"]} | comp: {sentiment_dict["compound"]}')
    #print()
    return sentiment_dict

    
def test_sentiment_analysis():
    initialize()
    session = create_session()
    tweets = session.query(Tweet).limit(100000).all()
    start = datetime.now()
    sentiments = [score(t.text) for t in tweets]
    end = datetime.now()
    delta = end - start
    for i in range(100):
        print(sentiments[i])
    print(f'Took {delta.seconds} seconds')