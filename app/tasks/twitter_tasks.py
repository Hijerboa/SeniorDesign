from sqlalchemy import asc, and_
from tasks.task_initializer import CELERY

from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from db.database_connection import create_session
from db.db_utils import create_single_object, get_or_create, get_single_object
from db.models import KeyRateLimit, TaskError, Tweet, SearchPhrase, TwitterUser, Task, twitter_api_token_type
from twitter_utils.user_gatherer import create_user_object
from tasks.machine_learning_tasks import run_get_tweet_sentiments

import random
import time

from datetime import datetime, timedelta
from pytz import timezone
my_tz = timezone('US/Eastern')
API_MANUAL_TIMEOUT = 3.25 #Manual timeout in seconds. Raise this if we're getting rate limited.
API_MONTHLY_TWEET_LIMIT = 10000000 #10,000,000 tweets/key/month

import logging
logger = logging.getLogger(__name__)

archive_api_key_id = get_secret('archive_api_key_id')
user_api_key_id = get_secret('user_api_key_id')

###
### Retrieve Tweets from archive
###

@CELERY.task()
def run_tweet_puller_archive(tweet_query: str, next_token, start_date, end_date, user_id):
    session = create_session(expire_on_commit=False)
    task = tweet_puller_archive(tweet_query, next_token, start_date, end_date, user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

@CELERY.task()
def rerun_tweet_puller_archive(task: Task, user_id):
    session = create_session(expire_on_commit=False)
    task = tweet_puller_archive(task.parameters['tweet_query'], task.parameters['next_token'], task.parameters['start_date'], task.parameters['end_date'], user_id)
    session.add(task)
    session.commit()
    res = task.run()
    return res

# Task class
class tweet_puller_archive(Task):
    def __init__(self, tweet_query: str, next_token, start_date, end_date, user_id):
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='tweet_puller_archive', parameters={'tweet_query':tweet_query, 'next_token':next_token, 'start_date':start_date, 'end_date':end_date})

    def run(self):    
        try:
            result = self.tweet_puller_archive(self.parameters['tweet_query'], self.parameters['next_token'], self.parameters['start_date'], self.parameters['end_date'], self.launched_by_id)
            self.complete = True
            return result
        except Exception as e: 
            session = create_session()
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            self.error = True
            session.commit()
            session.close()
            return str(e)

    def tweet_puller_archive(self, tweet_query: str, next_token, start_date, end_date, user_id):
        #logger.error(f'[{tweet_query}] Starting')
        session = create_session()

        db_search_phrase, created = get_or_create(session, SearchPhrase, search_phrase=tweet_query)
        tweet_count = 0
        twitter_users = []

        key = None
        # Get proper API token to use based on usage time and amount
        #logger.error(f"[{tweet_query}] Collecting Key")
        k = 1
        while key == None:
            key: KeyRateLimit = session.query(KeyRateLimit).\
                where(and_(KeyRateLimit.id == archive_api_key_id, KeyRateLimit.type == twitter_api_token_type.archive,  KeyRateLimit.last_query < datetime.now() - timedelta(seconds=API_MANUAL_TIMEOUT), KeyRateLimit.tweets_pulled < API_MONTHLY_TWEET_LIMIT - 100)).\
                order_by(asc(KeyRateLimit.tweets_pulled)).\
                first()
            if key is None:
                session.commit()
                # Check to see if we have any keys with tweets left:
                keys_avail = session.query(KeyRateLimit).\
                    where(and_(KeyRateLimit.id == archive_api_key_id, KeyRateLimit.type == twitter_api_token_type.archive, KeyRateLimit.tweets_pulled < API_MONTHLY_TWEET_LIMIT - 100)).\
                    all()
                #logger.error(f'[{tweet_query}] Waiting. Have {len(keys_avail)} valid keys')
                # If we do, just act normal
                if len(keys_avail) > 0:
                    wait = random.randint(1, int(2**k))
                    #logger.error(f'[{tweet_query}] Backing off for {wait} seconds')
                    time.sleep(wait)
                    if k < 3:
                        k+=1
                    pass #Either backoff here or wait, we can figure this out though
                else:
                    session.commit()
                    session.close()
                    logger.error(f'[{tweet_query}] API Limit hit on archive key {archive_api_key_id}. Closing.')
                    raise Exception(message=f'API Limit hit on archive key {archive_api_key_id}')

        session.commit()
        #key = keys[0]
        logger.error(f'[{tweet_query}] using key {key} - Last used {(datetime.now() - key.last_query).seconds} sec. ago')
        # Use correct secret ID
        twitter_api = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
        try:
            response = twitter_api.search_tweets_archive(tweet_query, start_date, end_date, next_token)
        except Exception as e:
            key.last_query = datetime.now()
            session.commit()
            session.close()
            raise e
        #logger.error(f'[{tweet_query}] Got a response')
        # Update API usage time to now
        key.last_query = datetime.now()
        #logger.error(f'[{tweet_query}] Setting last query time to {key.last_query}')
        #
        try:
            tweets = response['data']['data']
            # and update the number of tweets pulled
            key.tweets_pulled += len(tweets)

            # save to db
            session.commit()
            #logger.error(f'[{tweet_query}] Commited key fields change at {datetime.now()}')
            #
        except KeyError:

            session.commit()
            #logger.error(f'[{tweet_query}] Commited key fields change at {datetime.now()}')
            session.close()
            return '{0} tweets collected'.format(str(tweet_count))
        #logger.error(f'[{tweet_query}] Processing tweets')
        tweet_ids = []
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
                if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                    tweet_dict['reply'] = True
                    tweet_dict['reply_to_id'] = tweet['referenced_tweets'][0]['id']
                twitter_user = get_single_object(session, TwitterUser, id=tweet['author_id'])
                if twitter_user is None:
                    twitter_users.append(str(tweet['author_id']))
                    if len(twitter_users) == 100:
                        string = ','.join(twitter_users)
                        run_retrieve_users_info_by_ids.apply_async((string, user_id))
                        twitter_users = []
                tweet_object, created = get_or_create(session, Tweet, id=tweet['id'], defaults=tweet_dict)
                if created:
                    tweet_ids.append(tweet_object.id)
                tweet_object.search_phrases.append(db_search_phrase)
                session.commit()
                tweet_count += 1
            except KeyError:
                pass
        if not len(twitter_users) == 0:
            string = ','.join(twitter_users)
            run_retrieve_users_info_by_ids.apply_async((string, user_id))
        session.close()
        try:
            next_token = response['data']['meta']['next_token']
            run_tweet_puller_archive.apply_async((tweet_query, next_token, start_date, end_date, user_id))
        except KeyError:
            pass
        if len(tweet_ids) > 0:
            run_get_tweet_sentiments.apply_async((tweet_ids, 1,))
        return '{0} tweets collected'.format(str(tweet_count))

###
### Retrieve user info by id task (single)
###
@CELERY.task()
def run_retrieve_user_info_by_id(twitter_user_id: str, user_id):
    session = create_session(expire_on_commit=False)
    task = retrieve_user_info_by_id(twitter_user_id, user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

@CELERY.task()
def rerun_retrieve_user_info_by_id(task: Task, user_id):
    session = create_session(expire_on_commit=False)
    task = retrieve_user_info_by_id(task.parameters['twitter_user_id'], user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

# Task class
class retrieve_user_info_by_id(Task):
    def __init__(self, twitter_user_id: str, user_id):
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='retrieve_user_info_by_id', parameters={'twitter_user_id':twitter_user_id})

    def run(self):
        try:
            result = self.retrieve_user_info_by_username(self.parameters['twitter_user_id'])
            self.complete = True
            return result
        except Exception as e: 
            session = create_session()
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            self.error = True
            session.commit()
            session.close()
            return str(e)

    def retrieve_user_info_by_id(self, twitter_user_id: int):
        session = create_session()
        # Get proper API token to use based on usage time. Tweets pulled doesn't matter for getting user info.
        key = None
        while key == None:
            key = session.query(KeyRateLimit).\
                where(and_(KeyRateLimit.id == user_api_key_id, KeyRateLimit.type == twitter_api_token_type.non_archive,  KeyRateLimit.last_query < datetime.now() - timedelta(seconds=API_MANUAL_TIMEOUT))).\
                order_by(asc(KeyRateLimit.last_query)).\
                first()
            if key == None:
                pass #Either backoff here or wait, we can figure this out though

        session.commit()
        # Use correct secret ID
        twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
        try:
            user_data = twitter_api.get_user_by_id(twitter_user_id)['data']['data']
        except Exception as e:
            key.last_query = datetime.now()
            session.commit()
            session.close()
            raise e
        # Update API usage time to now and commit to db
        key.last_query = datetime.now()

        session.commit()

        create_user_object(user_data, session)
        session.commit()
        session.close()
        return 'User info collected'

###
### Retrieve user info by ids task (multiple)
###
@CELERY.task()
def run_retrieve_users_info_by_ids(user_ids: str, user_id):
    session = create_session(expire_on_commit=False)
    task = retrieve_users_info_by_ids(user_ids, user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

@CELERY.task()
def rerun_retrieve_users_info_by_ids(task: Task, user_id):
    session = create_session(expire_on_commit=False)
    task = retrieve_users_info_by_ids(task.parameters['user_ids'], user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

# Task Class
class retrieve_users_info_by_ids(Task):
    def __init__(self, user_ids: str, user_id):
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='retrieve_users_info_by_ids', parameters={'user_ids':user_ids})

    def run(self):
        try:
            result = self.retrieve_users_info_by_ids(self.parameters['user_ids'])
            self.complete = True
            return result
        except Exception as e: 
            session = create_session()
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            self.error = True
            session.commit()
            session.close()
            return str(e)

    def retrieve_users_info_by_ids(self, user_ids: str):
        session = create_session()
        # Get proper API token to use based on usage time. Tweets pulled doesn't matter for getting user info.
        key = None
        while key == None:
            key = session.query(KeyRateLimit).\
                where(and_(KeyRateLimit.id == user_api_key_id, KeyRateLimit.type == twitter_api_token_type.non_archive,  KeyRateLimit.last_query < datetime.now() - timedelta(seconds=API_MANUAL_TIMEOUT))).\
                order_by(asc(KeyRateLimit.last_query)).\
                first()
            if key == None:
                pass #Either backoff here or wait, we can figure this out though

        session.commit()
        # Use correct secret ID
        twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
        try:
            user_response = twitter_api.get_users_by_ids(user_ids)['data']['data']
        except Exception as e:
            key.last_query = datetime.now()
            session.commit()
            session.close()
            raise e
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


###
### User info by username task
###
@CELERY.task()
def run_retrieve_user_info_by_username(username: str, user_id):
    session = create_session(expire_on_commit=False)
    task = retrieve_user_info_by_username(username, user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

@CELERY.task()
def rerun_retrieve_user_info_by_username(task: Task, user_id):
    session = create_session(expire_on_commit=False)
    task = retrieve_user_info_by_username(task.parameters['username'], user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res

# Task class
class retrieve_user_info_by_username(Task):
    def __init__(self, username: str, user_id):
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='retrieve_user_info_by_username', parameters={'username':username})

    def run(self):
        try:
            result = self.retrieve_user_info_by_username(self.parameters['username'])
            self.complete = True
            return result
        except Exception as e: 
            session = create_session()
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            self.error = False
            session.commit()
            session.close()
            return str(e)

    def retrieve_user_info_by_username(self, username: str):
        session = create_session()
        # Get proper API token to use based on usage time. Tweets pulled doesn't matter for getting user info.
        key = None
        while key == None:
            key = session.query(KeyRateLimit).\
                where(and_(KeyRateLimit.id == user_api_key_id, KeyRateLimit.type == twitter_api_token_type.non_archive,  KeyRateLimit.last_query < datetime.now() - timedelta(seconds=API_MANUAL_TIMEOUT))).\
                order_by(asc(KeyRateLimit.last_query)).\
                first()
            if key == None:
                pass #Either backoff here or wait, we can figure this out though

        session.commit() 
        # Use correct secret ID
        twitter_api: TwitterAPI = TwitterAPI(get_secret('twitter_api_url'), get_secret(f'twitter_bearer_token_{key.id}'))
        try:
            user_data = twitter_api.get_user_by_username(username)['data']['data']
        except Exception as e:
            key.last_query = datetime.now()
            session.commit()
            session.close()
            raise e
        # Update API usage time to now and commit to db
        key.last_query = datetime.now()

        session.commit()

        
        create_user_object(user_data, session)
        session.commit()
        session.close()
        return 'User info collected'