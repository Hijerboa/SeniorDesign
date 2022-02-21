from sqlalchemy import asc, and_
from tasks.task_initializer import CELERY

from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from apis.propublica_api import ProPublicaAPI
from db.database_connection import create_session
from db.db_utils import get_or_create, get_single_object
from db.models import KeyRateLimit, Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, twitter_api_token_type
from twitter_utils.user_gatherer import create_user_object

from datetime import datetime, timedelta
from pytz import timezone
my_tz = timezone('US/Eastern')
API_MANUAL_TIMEOUT = 3 #Manual timeout in seconds. Raise this if we're getting rate limited.
API_TWEET_LIMIT = 10000000


@CELERY.task
def tweet_puller_archive(tweet_query: str, next_token, start_date, end_date):
    session = create_session()

    db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
    tweet_count = 0
    twitter_users = []

    keys = []
    # Get proper API token to use based on usage time and amount
    while len(keys) == 0:
        keys = session.query(KeyRateLimit).\
            where(and_(KeyRateLimit.type == twitter_api_token_type.archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT), KeyRateLimit.tweets_pulled < API_TWEET_LIMIT)).\
            with_for_update(skip_locked=True).\
            order_by(asc(KeyRateLimit.tweets_pulled)).\
            limit(1).\
            all()
        if len(keys) == 0:
            pass #Either backoff here or wait, we can figure this out though
    key = keys[0]
    # Use correct secret ID
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
    response = twitter_api.search_tweets_archive(tweet_query, start_date, end_date, next_token)
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
        return '{0} tweets collected'.format(str(tweet_count))
    for tweet in tweets:
        try:
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
                retrieve_users_info_by_ids.apply_async((string,))
                twitter_users = []
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()
        tweet_count += 1
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        retrieve_users_info_by_ids.apply_async((string,))
    session.close()
    try:
        next_token = response['data']['meta']['next_token']
        tweet_puller_archive.apply_async((tweet_query, next_token, start_date, end_date,))
    except KeyError:
        pass
    return '{0} tweets collected'.format(str(tweet_count))


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
