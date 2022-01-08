from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.sql.expression import func
import db.database_connection as db
from db.models import Tweet
from datetime import datetime

### This is slow bc it makes the analyzer every time, but fuck it.
def score(document):
    sia_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sia_obj.polarity_scores(document)
    #print('--------------------------------------------------')
    #print(document)
    #print()
    #print(f'+: {sentiment_dict["pos"]}| -: {sentiment_dict["neg"]}| o: {sentiment_dict["neu"]} | comp: {sentiment_dict["compound"]}')
    #print()
    return sentiment_dict

def test():
    start = datetime.now()
    db.initialize()
    session = db.create_session()
    tweets = session.query(Tweet).limit(10000).all()
    sentiments = []
    for t in tweets:
        sentiments.append(score(t.text))
    for i in range(100):
        print(sentiments[i])
    end = datetime.now()
    delta = end - start
    print(f'took {delta.seconds} seconds.')
    
