from tasks.task_initializer import CELERY

from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from apis.propublica_api import ProPublicaAPI
from db.database_connection import create_session
from db.db_utils import get_or_create, get_single_object
from db.models import Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, User
from twitter_utils.user_gatherer import create_user_object

from datetime import datetime, timedelta
from pytz import timezone
my_tz = timezone('US/Eastern')

@CELERY.task
def tweet_puller_stream(tweet_query: str, next_token, start_date, end_date):
    session = create_session()
    twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
    tweet_count = 0
    twitter_users = []
    response = twitter_api.search_tweets(tweet_query, start_date, end_date, next_token)
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
                retrieve_users_info_by_ids.apply_async((string,), countdown=4)
                twitter_users = []
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()
        tweet_count += 1
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        retrieve_users_info_by_ids.apply_async((string,), countdown=4)
    session.close()
    try:
        next_token = response['data']['meta']['next_token']
        tweet_puller_stream.apply_async((tweet_query, next_token, start_date, end_date,), countdown=4)
    except KeyError:
        pass
    return '{0} tweets collected'.format(str(tweet_count))


@CELERY.task
def tweet_puller_archive(tweet_query: str, next_token, start_date, end_date):
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
                retrieve_users_info_by_ids.apply_async((string,), countdown=4)
                twitter_users = []
        tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
        tweet_object.search_phrases.append(db_search_phrase)
        session.commit()
        tweet_count += 1
    if not len(twitter_users) == 0:
        string = ','.join(twitter_users)
        retrieve_users_info_by_ids.apply_async((string,), countdown=4)
    session.close()
    try:
        next_token = response['data']['meta']['next_token']
        tweet_puller_archive.apply_async((tweet_query, next_token, start_date, end_date,), countdown=4)
    except KeyError:
        pass
    return '{0} tweets collected'.format(str(tweet_count))


@CELERY.task()
def retrieve_user_info_by_id(user_id: int):
    session = create_session()
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_data = twitter_api.get_user_by_id(user_id)['data']['data']
    create_user_object(user_data, session)
    session.commit()
    session.close()
    return 'User info collected'


@CELERY.task()
def retrieve_users_info_by_ids(user_ids: str):
    session = create_session()
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
def retrieve_user_info_by_username(username: str):
    session = create_session()
    twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret('twitter_bearer_token'))
    user_data = twitter_api.get_user_by_username(username)['data']['data']
    create_user_object(user_data, session)
    session.commit()
    session.close()
    return 'User info collected'
