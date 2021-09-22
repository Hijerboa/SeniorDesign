from apis.twitter_api import TwitterAPI
from util.cred_handler import get_secret


def get_tweets():
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))

    tweets = twitter_api.search_tweets('impeach biden')
    print(tweets)

    for i in range(50):
        next_token = tweets['data']['meta']['next_token']
        tweets = twitter_api.search_tweets('impeach biden', next_token=next_token)
        print(tweets)
