''' Tasks related to celery functions '''
import time
import random
import datetime
from kombu import Queue

from celery import Celery, current_task
from celery.exceptions import CeleryError
from celery.result import AsyncResult
from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from apis.propublica_api import ProPublicaAPI
from db.database_connection import initialize, create_session
from db.db_utils import get_or_create, get_single_object
from db.models import Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes
from twitter_utils.user_gatherer import create_user_object

REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://{0}:{1}@rabbit//'.format(get_secret("RABBITMQ_USER"), get_secret("RABBITMQ_PASS"))

task_routes = {
    'server.tasks.tweet_puller': {'queue': 'long_task'},
    'server.tasks.retrieve_user_info_by_id': {'queue': 'short_task'},
    'server.tasks.retrieve_user_info_by_username': {'queue': 'short_task'},
    'server.tasks.retrieve_users_info_by_ids': {'queue': 'short_task'},
    'server.tasks.get_bill_data_by_congress': {'queue': 'long_task'},
    'server.tasks.add': {'queue': 'short_task'}
}


def route_task(name, args, kwargs, options, task=None, **kw):
    if name == 'server.tasks.tweet_puller':
        return {'queue': 'long_task', 'routing_key': 'tweet.puller'}
    elif name == 'server.tasks.retrieve_user_info_by_id':
        return {'queue': 'short_task', 'routing_key': 'user.puller'}


CELERY = Celery('tasks',
            backend=REDIS_URL,
            broker=BROKER_URL)

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'msgpack'
CELERY.conf.task_routes = task_routes


initialize()


def get_job(job_id):
    '''
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(job_id, app=CELERY)


@CELERY.task
def tweet_puller(tweet_query: str, useless):
    print(tweet_query)
    session = create_session()
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))

    response = twitter_api.search_tweets(tweet_query)
    db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
    tweets = response['data']['data']
    tweet_list = []
    twitter_users = []
    for tweet in tweets:

        tweet_dict = {
            'author_id': tweet['author_id'],
            'created_at': datetime.datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            'text': tweet['text'],
            'source': tweet['source'],
            'lang': tweet['lang'],
            'retweets': tweet['public_metrics']['retweet_count'],
            'likes': tweet['public_metrics']['like_count'],
            'replies': tweet['public_metrics']['reply_count'],
            'quote_count': tweet['public_metrics']['quote_count']
        }
        try:
            if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                tweet_dict['reply'] = True
                tweet_dict['reply_to_id'] = tweet['referenced_tweets'][0]['id']
        except KeyError:
            pass
        twitter_user = get_single_object(session, TwitterUser, id=tweet['author_id'])
        if twitter_user is None:
            twitter_users.append(str(tweet['author_id']))
            if len(twitter_users) == 100:
                string = ','.join(twitter_users)
                retrieve_users_info_by_ids.delay(string)
                twitter_users = []
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()

    for i in range(50000):
        time.sleep(2.7)
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
                    'retweets': tweet['public_metrics']['retweet_count'],
                    'likes': tweet['public_metrics']['like_count'],
                    'replies': tweet['public_metrics']['reply_count'],
                    'quote_count': tweet['public_metrics']['quote_count']
                }
                try:
                    if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                        tweet_dict['reply'] = True
                        tweet_dict['reply_to_id'] = tweet['referenced_tweets'][0]['id']
                except KeyError:
                    pass
                twitter_user = get_single_object(session, TwitterUser, id=tweet['author_id'])
                if twitter_user is None:
                    twitter_users.append(str(tweet['author_id']))
                    if len(twitter_users) == 100:
                        string = ','.join(twitter_users)
                        retrieve_users_info_by_ids.delay(string)
                        twitter_users = []
                tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
                tweet_object.search_phrases.append(db_search_phrase)
        except KeyError:
            break
        session.commit()
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        retrieve_users_info_by_ids.delay(string)
    session.close()
    return "Hello there"


@CELERY.task()
def retrieve_user_info_by_id(user_id: int, useless):
    time.sleep(3)
    session = create_session()
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_data = twitter_api.get_user_by_id(user_id)['data']['data']
    create_user_object(user_data, session)
    session.close()


@CELERY.task()
def retrieve_users_info_by_ids(user_ids: str, useless):
    time.sleep(2.5)
    session = create_session()
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_response = twitter_api.get_users_by_ids(user_ids)['data']['data']
    for user_data in user_response:
        create_user_object(user_data, session)
    session.close()


@CELERY.task()
def retrieve_user_info_by_username(username: str, useless):
    time.sleep(3)
    session = create_session()
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_data = twitter_api.get_user_by_username(username)['data']['data']
    create_user_object(user_data, session)
    session.close()


@CELERY.task()
def get_bill_data_by_congress(congress_id: int, congress_chamber: str, useless):
    initialize()
    session = create_session()
    current_offset = 0
    valid_results = True
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))

    while valid_results:
        results = pro_publica_api.get_recent_bills(congress_id, congress_chamber, current_offset)
        if results['data']['results'][0]['num_results'] == 0:
            valid_results = False
            break
        bills = results['data']['results'][0]['bills']
        for bill in bills:
            co_sponsor_parties = bill['cosponsors_by_party']
            committee_codes = bill['committee_codes']
            subcommittee_codes = bill['subcommittee_codes']
            bad_items = ['sponsor_title', 'sponsor_name', 'sponsor_state', 'sponsor_uri', 'cosponsors_by_party',
                         'committee_codes', 'subcommittee_codes', 'bill_uri']
            for item in bad_items:
                bill.pop(item)
            if 'R' in co_sponsor_parties.keys():
                bill['rep_cosponsors'] = co_sponsor_parties['R']
            if 'D' in co_sponsor_parties.keys():
                bill['dem_cosponsors'] = co_sponsor_parties['D']
            bill['congress'] = congress_id
            object, created = get_or_create(session, Bill, bill_id=bill['bill_id'], defaults=bill)
            session.commit()
            for committee_code in committee_codes:
                committee_object, created = get_or_create(session, CommitteeCodes, committee_code=committee_code)
                session.commit()
                object.committee_codes.append(committee_object)
            for subcommittee_code in subcommittee_codes:
                subcommittee_object, created = get_or_create(session, SubcommitteeCodes,
                                                             subcommittee_code=subcommittee_code)
                session.commit()
                object.sub_committee_codes.append(subcommittee_object)
        current_offset += 20
        session.commit()