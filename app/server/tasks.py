''' Tasks related to celery functions '''
import time
import datetime
from celery import Celery, current_task, uuid
from celery.exceptions import CeleryError
from celery.result import AsyncResult
from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from apis.propublica_api import ProPublicaAPI
from db.database_connection import initialize, create_session
from db.db_utils import get_or_create, get_single_object, create_single_object
from db.models import Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, User
from twitter_utils.user_gatherer import create_user_object
from util.task_utils import create_task_db_object

REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://{0}:{1}@rabbit//'.format(get_secret("RABBITMQ_USER"), get_secret("RABBITMQ_PASS"))

task_routes = {
    'server.tasks.tweet_puller_stream': {'queue': 'twitter_stream'},
    'server.tasks.tweet_puller_archive': {'queue': 'twitter_archive'},
    'server.tasks.retrieve_user_info_by_id': {'queue': 'twitter_users'},
    'server.tasks.retrieve_user_info_by_username': {'queue': 'twitter_users'},
    'server.tasks.retrieve_users_info_by_ids': {'queue': 'twitter_users'},
    'server.tasks.get_bill_data_by_congress': {'queue': 'propublica_tasks'},
}

CELERY = Celery('tasks',
            backend=REDIS_URL,
            broker=BROKER_URL)

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'msgpack'
CELERY.conf.task_routes = task_routes
CELERY.conf.task_track_started = True


initialize()


def get_job(job_id):
    '''
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(job_id, app=CELERY)


# Each of these tasks has a parameter named "useless". Don't touch it. It is used in order to make the apply async
# method work from celery. Without it, things get messy. No touchie.


@CELERY.task
def tweet_puller_stream(tweet_query: str, next_token, useless):
    session = create_session()
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
    tweet_count = 0
    twitter_users = []
    response = twitter_api.search_tweets(tweet_query, next_token)
    try:
        tweets = response['data']['data']
    except KeyError:
        session.commit()
        session.close()
        return '{0} tweets collected'.format(str(tweet_count))
    for tweet in tweets:
        try:
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
        except KeyError:
            pass
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
                task_id = uuid()
                retrieve_users_info_by_ids.apply_async((string, 0), task_id=task_id)
                twitter_users = []
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()
        tweet_count += 1
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        task_id = uuid()
        retrieve_users_info_by_ids.apply_async((string, 0), task_id=task_id)
    session.close()
    next_token = response['data']['meta']['next_token']
    tweet_puller_stream.apply_async((tweet_query, next_token, 0), countdown=3)
    return '{0} tweets collected'.format(str(tweet_count))


@CELERY.task
def tweet_puller_archive(tweet_query: str, next_token, start_date, end_date, useless):
    session = create_session()
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
    tweet_count = 0
    twitter_users = []
    response = twitter_api.search_tweets_archive(tweet_query, start_date, end_date, next_token)
    try:
        tweets = response['data']['data']
    except KeyError:
        session.commit()
        session.close()
        return '{0} tweets collected'.format(str(tweet_count))
    for tweet in tweets:
        try:
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
        except KeyError:
            pass
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
                task_id = uuid()
                retrieve_users_info_by_ids.apply_async((string, 0), task_id=task_id)
                twitter_users = []
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()
        tweet_count += 1
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        task_id = uuid()
        retrieve_users_info_by_ids.apply_async((string, 0), task_id=task_id)
    session.close()
    next_token = response['data']['meta']['next_token']
    tweet_puller_archive.apply_async((tweet_query, next_token, start_date, end_date, 0), countdown=3)
    return '{0} tweets collected'.format(str(tweet_count))


@CELERY.task()
def retrieve_user_info_by_id(user_id: int, useless):
    session = create_session()
    time.sleep(3)
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_data = twitter_api.get_user_by_id(user_id)['data']['data']
    create_user_object(user_data, session)
    session.commit()
    session.close()
    return 'User info collected'


@CELERY.task()
def retrieve_users_info_by_ids(user_ids: str, useless):
    session = create_session()
    time.sleep(2.5)
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_response = twitter_api.get_users_by_ids(user_ids)['data']['data']
    user_num = 0
    for user_data in user_response:
        create_user_object(user_data, session)
        user_num += 1
    session.commit()
    session.close()
    return 'User info collected for {0} users'.format(str(user_num))


@CELERY.task()
def retrieve_user_info_by_username(username: str, useless):
    session = create_session()
    time.sleep(3)
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_data = twitter_api.get_user_by_username(username)['data']['data']
    create_user_object(user_data, session)
    session.commit()
    session.close()
    return 'User info collected'


@CELERY.task()
def get_bill_data_by_congress(congress_id: int, congress_chamber: str, useless):
    session = create_session()
    task_object: Task = get_single_object(session, Task, task_id=current_task.request.id)
    task_object.status = 'STARTED'
    task_object.message = 'Task has started to be run by the worker. This may take a while.'
    session.commit()
    num_bills = 0
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
            num_bills += 1
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
    task_object.status = 'SUCCESS'
    task_object.message = 'Task has successfully been completed. {0} bills collected'.format(str(num_bills))
    session.commit()
    return '{0} bills collected'.format(str(num_bills))