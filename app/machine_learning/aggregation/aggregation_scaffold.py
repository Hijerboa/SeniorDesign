import numpy as np
from db.database_connection import create_session
from db.models import Tweet, TwitterUser, CongressMemberData, Bill

CONF_THRESHOLD = 0.7
NEG_THRESHOLD = -0.5
POS_THRESHOLD = 0.5

def get_tweets(bill_id: str):
    """Returns all tweets for a specified bill and their user objects

    Args:
        bill_id (str): Bill ID

    Returns:
        set(): Set of tuples
        Each tuple contains a tweet object and it's cooresponding user object
        
    Yes I know this is memory inefficient. It reduces database calls. I don't fucking care.
    """
    
    all_tweets = set()
    all_users = [] # Done as an array to play nice with SQLAlchemy
    users_dict = {}
    
    session = create_session(expire_on_commit=False)
    
    bill = session.query(Bill).filter(Bill.bill_id==bill_id).first()
    for phrase in bill.keywords:
        tweets = session.query(Tweet).where(Tweet.search_phrases.contains(phrase)).all()
        for tweet in tweets:
            if tweet not in all_tweets:
                all_tweets.add(tweet)
                if tweet.author_id not in all_users:
                    all_users.append(tweet.author_id)

    user_objects = session.query(TwitterUser).filter(TwitterUser.id.in_(all_users)).all()
    for user_object in user_objects:
        users_dict[user_object.id] = user_object
    
    tweet_users_tuples = set()
    for tweet in all_tweets:
        tuple = (tweet, users_dict[tweet.author_id])
        tweet_users_tuples.add(tuple)
    
    session.close()
    return tweet_users_tuples


def get_flat_sentiment(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    analyzed_tweets = 0
    
    for tuple in tweets:
        tweet = tuple[0] # Get the tweet from the tuple
        if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
            analyzed_tweets += 1
            if tweet.sentiment is None:
                continue
            if tweet.sentiment > POS_THRESHOLD:
                total_positive += 1
            elif tweet.sentiment < NEG_THRESHOLD:
                total_negative += 1
            else:
                total_neutral += 1
            
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative
    }

    return results_dict


def verified_user_sentiment(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    analyzed_tweets = 0
    
    for tuple in tweets:
        tweet = tuple[0]
        user = tuple[1]
        if user.verified:
            if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
                analyzed_tweets += 1
                if tweet.sentiment is None:
                    continue
                if tweet.sentiment > POS_THRESHOLD:
                    total_positive += 1
                elif tweet.sentiment < NEG_THRESHOLD:
                    total_negative += 1
                else:
                    total_neutral += 1
    
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative
    }

    return results_dict


def politician_sentiment(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    analyzed_tweets = 0
    
    congress_usernames = set()
    
    session = create_session()
    
    congress_tuples = session.query(CongressMemberData.twitter_account).all()
    
    for tuple in congress_tuples:
        if tuple[0] is not None:
            if tuple[0] not in congress_usernames:
                congress_usernames.add(tuple[0])
                
    
    for tuple in tweets:
        tweet = tuple[0]
        user = tuple[1]
        if user.display_name in congress_usernames:
            if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
                analyzed_tweets += 1
                if tweet.sentiment is None:
                    continue
                if tweet.sentiment > POS_THRESHOLD:
                    total_positive += 1
                elif tweet.sentiment < NEG_THRESHOLD:
                    total_negative += 1
                else:
                    total_neutral += 1
    
    results_dict = {
        'total_tweets': len(tweets),
        'analyzed_tweets': analyzed_tweets,
        'total_positive': total_positive,
        'total_neutral': total_neutral,
        'total_negative': total_negative
    }
    
    session.close()

    return results_dict


def more_than_average_likes(tweets, confidence_thresholding=False):
    
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    weighted_positive = 0
    weighted_neutral = 0
    weighted_negative = 0
    analyzed_tweets = 0
    
    likes = [tuple[0].likes for tuple in tweets]
        
    likes_mean = np.mean(likes)
    likes_std = np.std(likes)
    
    for tuple in tweets:
        tweet = tuple[0]
        weight = 1 + (tweet.likes - likes_mean) / likes_std
        if (confidence_thresholding and tweet.sentiment_confidence is not None and tweet.sentiment_confidence >= CONF_THRESHOLD) or (not confidence_thresholding):
            analyzed_tweets += 1
            if tweet.sentiment is None:
                continue
            if tweet.sentiment > POS_THRESHOLD:
                total_positive += 1
                weighted_positive += 1 * weight
            elif tweet.sentiment < NEG_THRESHOLD:
                total_negative += 1
                weighted_negative += 1 * weight
            else:
                total_neutral += 1
                weighted_neutral += 1 * weight
                
        results_dict = {
            'total_tweets': len(tweets),
            'analyzed_tweets': analyzed_tweets,
            'total_positive': total_positive,
            'total_neutral': total_neutral,
            'total_negative': total_negative,
            'weighted_positive': weighted_positive,
            'weighted_neutral': weighted_neutral,
            'weighted_negative': weighted_negative
        }

    return results_dict
