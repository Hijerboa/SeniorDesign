from sqlalchemy import asc, and_
from tasks.task_initializer import CELERY

from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI, TwitterAPIError
from db.database_connection import create_session
from db.db_utils import get_or_create, get_single_object, create_single_object
from db.models import KeyRateLimit, Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, twitter_api_token_type, TaskError
from twitter_utils.user_gatherer import create_user_object

from datetime import datetime, timedelta
from pytz import timezone
my_tz = timezone('US/Eastern')
# TODO: Pull the below from a environment variable for ease of editing because we're good software engineers
API_MANUAL_TIMEOUT = 3 #Manual timeout in seconds. Raise this if we're getting rate limited.

from logging import getLogger

logger = getLogger(__name__)


@CELERY.task
def tweet_puller_archive(task_id: int):
    session = create_session()
    task_object: Task = get_single_object(session, Task, id=task_id)
    db_search_phrase = get_single_object(session, SearchPhrase, search_phrase=task_object.parameters['tweet_query'])
    twitter_users = []

    keys = []
    # Get proper API token to use based on usage time and amount
    while len(keys) == 0:
        keys = session.query(KeyRateLimit).\
            where(and_(KeyRateLimit.type == twitter_api_token_type.archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT))).\
            with_for_update(skip_locked=True).\
            order_by(asc(KeyRateLimit.tweets_pulled)).\
            limit(1).\
            all()
        if len(keys) == 0:
            pass #Either backoff here or wait, we can figure this out though
    key = keys[0]
    # Use correct secret ID
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
    try:
        response = twitter_api.search_tweets_archive(task_object.parameters['tweet_query'], task_object.parameters['start_date'], task_object.parameters['end_date'], task_object.parameters['next_token'])
    except TwitterAPIError as e:
        create_single_object(session, TaskError, task_id=task_object.id, description=e)
        task_object.error = True
        session.commit()
        session.close()
        return
    # Update API usage time to now
    key.last_query = datetime.now()
    #
    try:
        tweets = response['data']['data']
        # and update the number of tweets pulled
        key.tweets_pulled += len(tweets)
        # save to db
        session.commit()
        #
    except KeyError:
        session.commit()
        session.close()
        return
    for tweet in tweets:
        try:
            # Extract the information we care about from the API here
            tweet_dict = {
                'author_id': tweet['author_id'],
                'created_at': datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
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
        # If tweets are referenced by another tweet; throw an exception and pass if not becauase EZ
        try:
            if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                tweet_dict['reply'] = True
                tweet_dict['reply_to_id'] = tweet['referenced_tweets'][0]['id']
        except KeyError:
            pass
        # Check if we've gathered that user's info, if not queue it for collection
        twitter_user = get_single_object(session, TwitterUser, id=tweet['author_id'])
        
        if twitter_user is None:
            twitter_users.append(str(tweet['author_id']))
            if len(twitter_users) == 100:
                string = ','.join(twitter_users)
                retrieve_users_info_by_ids.apply_async((string,))
                twitter_users = []
        
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        
        session.commit()
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        retrieve_users_info_by_ids.apply_async((string,))
    try:
        task_object.parameters['next_token'] = response['data']['meta']['next_token']
        session.commit()
        tweet_puller_archive.apply_async((task_id,))
    except KeyError:
        task_object.complete = True
        session.commit()
    session.close()
    return f'{len(tweets)} tweets collected'


@CELERY.task()
def retrieve_user_info_by_id(user_id: int):
    session = create_session()
    # Get proper API token to use based on usage time. Tweets pulled doesn't matter for getting user info.
    keys = []
    while len(keys) == 0:
        keys = session.query(KeyRateLimit).\
            where(and_(KeyRateLimit.type == twitter_api_token_type.non_archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT))).\
            with_for_update(skip_locked=True).\
            order_by(asc(KeyRateLimit.last_query)).\
            limit(1).\
            all()
        if len(keys) == 0:
            pass #Either backoff here or wait, we can figure this out though
    key = keys[0]
    # Use correct secret ID
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
    user_data = twitter_api.get_user_by_id(user_id)['data']['data']
    # Update API usage time to now and commit to db
    key.last_query = datetime.now()
    session.commit()

    create_user_object(user_data, session)
    session.commit()
    session.close()
    return 'User info collected'


@CELERY.task()
def retrieve_users_info_by_ids(user_ids: str):
    session = create_session()
    # Get proper API token to use based on usage time. Tweets pulled doesn't matter for getting user info.
    keys = []
    while len(keys) == 0:
        keys = session.query(KeyRateLimit).\
            where(and_(KeyRateLimit.type == twitter_api_token_type.non_archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT))).\
            with_for_update(skip_locked=True).\
            order_by(asc(KeyRateLimit.last_query)).\
            limit(1).\
            all()
        if len(keys) == 0:
            pass #Either backoff here or wait, we can figure this out though
    key = keys[0]  
    # Use correct secret ID
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
    user_response = twitter_api.get_users_by_ids(user_ids)['data']['data']
    # Update API usage time to now and commit to db
    key.last_query = datetime.now()
    session.commit()

    user_num = 0
    for user_data in user_response:
        create_user_object(user_data, session)
        user_num += 1
    session.commit()
    session.close()
    return 'User info collected for {0} users'.format(str(user_num))


@CELERY.task()
def retrieve_user_info_by_username(username: str):
    session = create_session()
    # Get proper API token to use based on usage time. Tweets pulled doesn't matter for getting user info.
    keys = []
    while len(keys) == 0:
        keys = session.query(KeyRateLimit).\
            where(and_(KeyRateLimit.type == twitter_api_token_type.non_archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT))).\
            with_for_update(skip_locked=True).\
            order_by(asc(KeyRateLimit.last_query)).\
            limit(1).\
            all()
        if len(keys) == 0:
            pass #Either backoff here or wait, we can figure this out though
    key = keys[0]   
    # Use correct secret ID
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
    user_data = twitter_api.get_user_by_username(username)['data']['data']
    # Update API usage time to now and commit to db
    key.last_query = datetime.now()
    session.commit()

    create_user_object(user_data, session)
    session.commit()
    session.close()
    return 'User info collected'
