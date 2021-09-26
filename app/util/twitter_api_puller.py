from apis.twitter_api import TwitterAPI
from util.cred_handler import get_secret
from db.database_connection import get_connection
from db.database_methods import insert_tweets
from db.models import Tweet
from time import sleep


def get_tweets():
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))

    response = twitter_api.search_tweets('impeach biden')
    tweets = response['data']['data']
    tweet_list = []
    for tweet in tweets:
        tweet['id'] = str(tweet['id']).rjust(24, "0")
        tweet_object = Tweet(**tweet)
        tweet_list.append(tweet_object.mongo())

    print(tweets)

    db = get_connection()

    insert_tweets(tweet_list, db)

    for i in range(5000):
        sleep(2)
        next_token = response['data']['meta']['next_token']
        response = twitter_api.search_tweets('impeach biden', next_token=next_token)
        tweet_list = []
        tweets = response['data']['data']
        for tweet in tweets:
            tweet['id'] = str(tweet['id']).rjust(24, "0")
            tweet_object = Tweet(**tweet)
            tweet_list.append(tweet_object.mongo())
        insert_tweets(tweet_list, db)
