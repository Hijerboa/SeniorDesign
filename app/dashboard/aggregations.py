from db import database_connection as conn
from sqlalchemy.sql import func
from db.models import *
from functools import reduce

NEG_THRESHOLD = -0.5
POS_THRESHOLD = 0.5
LOGGING = True

conn.initialize()

class Result:
    def __init__(self, count_pos, count_neg, count_neu, percent_pos, percent_neg, percent_neu):
        self.count_pos = count_pos
        self.count_neg = count_neg
        self.count_neu = count_neu
        self.percent_pos = percent_pos
        self.percent_neg = percent_neg
        self.percent_neu = percent_neu

def get_result(tweets):
    size = len(tweets)
    count_pos = len(list(filter(lambda x: False if x.sentiment == None else x.sentiment > POS_THRESHOLD, tweets)))
    count_neg = len(list(filter(lambda x: False if x.sentiment == None else x.sentiment < NEG_THRESHOLD, tweets)))
    count_neu = size - count_pos - count_neg
    percent_pos = count_pos / size
    percent_neg = count_neg / size
    percent_neu = 1 - percent_pos - percent_neg
    if LOGGING:
        print(f"# OF TWEETS | {size}")
        print(f"POSITIVE | {count_pos}     % POSITIVE | {round(percent_pos, 2)}")
        print(f"NEGATIVE | {count_neg}     % NEGATIVE | {round(percent_neg, 2)}")
        print(f"NEUTRAL | {count_neu}     % NEUTRAL | {round(percent_neu, 2)}\n")
    
    return Result(count_pos, count_neg, count_neu, percent_pos, percent_neg, percent_neu)

def get_keywords(bill_id):
    session = conn.create_session()
    bills = session.query(Bill).where(Bill.bill_id == bill_id).all()
    result = [] if len(bills) == 0 else bills[0].keywords
    session.close()
    if LOGGING:
        print(f"USING BILL ID: {bill_id}")
    return result

def flat_average(keywords):
    session = conn.create_session()
    tweets = set()
    for keyword in keywords:
        returned_tweets = session.query(Tweet).where(Tweet.search_phrases.contains(keyword)).all()
        for tweet in returned_tweets:
            tweets.add(tweet)
    result = get_result(tweets)
    session.close()
    return result

def verified_users(keywords):
    session = conn.create_session()
    tweets = set()
    for keyword in keywords:
        returned_tweets = session.query(Tweet).where(Tweet.search_phrases.contains(keyword)).join(TwitterUser, TwitterUser.id == Tweet.author_id).filter(TwitterUser.verified)
        for tweet in returned_tweets:
            tweets.add(tweet)
    result = get_result(tweets)
    session.close()
    return result

def retweet_log_scaling():
    """
    @Nathan couldn't remember how you wanted to do this one
    """
    pass

def only_politicians(keywords):
    """
    This one currently hangs, I think my joins are wrong or it's taking too long
    """
    session = conn.create_session()
    tweets = set()
    for keyword in keywords:
        returned_tweets = session.query(Tweet).where(Tweet.search_phrases.contains(keyword)).join(TwitterUser, TwitterUser.id == Tweet.author_id).join(CongressMemberData, CongressMemberData.twitter_account == TwitterUser.display_name).all()
        for tweet in returned_tweets:
            tweets.add(tweet)
    result = get_result(tweets)
    session.close()
    return result

def confidence_filtering(keywords, confidence):
    session = conn.create_session()
    tweets = set()
    for keyword in keywords:
        returned_tweets = session.query(Tweet).where(Tweet.search_phrases.contains(keyword)).filter(Tweet.sentiment_confidence > confidence)
        for tweet in returned_tweets:
            tweets.add(tweet)
    result = get_result(tweets)
    session.close()
    return result

def metric_boosting():
    """
    Weight added to tweets with higher Like + Retweet counts
    """
    pass

def get_ratiod():
    """
    lol
    """
    pass