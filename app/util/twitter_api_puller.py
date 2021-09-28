from apis.twitter_api import TwitterAPI
from util.cred_handler import get_secret
from db.database_connection import get_connection
from db.database_methods import insert_tweets
from db.models import Tweet
from time import sleep


def get_tweets(query_string: str):
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))

    response = twitter_api.search_tweets(query_string)
    tweets = response['data']['data']
    tweet_list = []
    for tweet in tweets:
        tweet['id'] = str(tweet['id']).rjust(24, "0")
        tweet['phrase'] = query_string
        tweet_object = Tweet(**tweet)
        tweet_list.append(tweet_object.mongo())

    print(tweets)

    db = get_connection()

    insert_tweets(tweet_list, db)

    for i in range(50000):
        sleep(2)
        try:
            next_token = response['data']['meta']['next_token']
            response = twitter_api.search_tweets(query_string, next_token=next_token)
            tweet_list = []
            tweets = response['data']['data']
            for tweet in tweets:
                tweet['id'] = str(tweet['id']).rjust(24, "0")
                tweet['phrase'] = query_string
                tweet_object = Tweet(**tweet)
                tweet_list.append(tweet_object.mongo())
            insert_tweets(tweet_list, db)
        except KeyError:
            break
