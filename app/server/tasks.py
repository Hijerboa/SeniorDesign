''' Tasks related to celery functions '''
import time
import random
import datetime

from celery import Celery, current_task
from celery.exceptions import CeleryError
from celery.result import AsyncResult
from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from db.database_connection import initialize, create_session
from db.db_utils import get_or_create
from db.models import Tweet, SearchPhrase

REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://{0}:{1}@rabbit//'.format(get_secret("RABBITMQ_USER"), get_secret("RABBITMQ_PASS"))

CELERY = Celery('tasks',
            backend=REDIS_URL,
            broker=BROKER_URL)

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'msgpack'

initialize()

def get_job(job_id):
    '''
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(job_id, app=CELERY)


@CELERY.task()
def tweet_puller(tweet_query: str):
    print(tweet_query)
    session = create_session()
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))

    response = twitter_api.search_tweets(tweet_query)
    db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
    tweets = response['data']['data']
    tweet_list = []
    for tweet in tweets:
        tweet_dict = {
            'author_id': tweet['author_id'],
            'created_at': datetime.datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            'text': tweet['text'],
            'source': tweet['source'],
            'lang': tweet['lang'],
        }
        try:
            if tweet['text'].startswith('RT'):
                tweet_dict['retweet'] = True
                tweet_dict['retweet_original_id'] = tweet['referenced_tweets'][0]['id']
        except KeyError:
            pass
        try:
            if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                tweet_dict['reply'] = True
                tweet_dict['reply_to_id'] = tweet['referenced_tweets'][0]['id']
        except KeyError:
            pass
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()

    for i in range(50000):
        time.sleep(2)
        try:
            next_token = response['data']['meta']['next_token']
            response = twitter_api.search_tweets(tweet_query, next_token=next_token)
            tweets = response['data']['data']
            tweet_list = []
            for tweet in tweets:
                tweet_dict = {
                    'author_id': tweet['author_id'],
                    'created_at': datetime.datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    'text': tweet['text'],
                    'source': tweet['source'],
                    'lang': tweet['lang'],
                }
                try:
                    if tweet['text'].startswith('RT'):
                        tweet_dict['retweet'] = True
                        tweet_dict['retweet_original_id'] = tweet['referenced_tweets'][0]['id']
                except KeyError:
                    pass
                try:
                    if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                        tweet_dict['reply'] = True
                        tweet_dict['reply_to_id'] = tweet['referenced_tweets'][0]['id']
                except KeyError:
                    pass
                tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
                tweet_object.search_phrases.append(db_search_phrase)
        except KeyError:
            break
        session.commit()
