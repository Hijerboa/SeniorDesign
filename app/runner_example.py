from db.database_connection import initialize, create_session
from sqlalchemy import asc, and_
from tasks.task_initializer import CELERY

from util.cred_handler import get_secret
from apis.twitter_api import TwitterAPI
from apis.propublica_api import ProPublicaAPI
from db.database_connection import create_session
from db.db_utils import create_single_object, get_or_create, get_single_object
from db.models import KeyRateLimit, TaskError, Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, twitter_api_token_type
from twitter_utils.user_gatherer import create_user_object

import random
import time

from datetime import datetime, timedelta

import logging
API_MANUAL_TIMEOUT = 3 #Manual timeout in seconds. Raise this if we're getting rate limited.
API_MONTHLY_TWEET_LIMIT = 10000000 #10,000,000 tweets/key/month

logger = logging.getLogger('FUCK THIS HOLY SHIT')

def ex():
    initialize()
    session = create_session() 
    keys = session.query(KeyRateLimit).\
                    where(and_(KeyRateLimit.type == twitter_api_token_type.archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT), KeyRateLimit.tweets_pulled < API_MONTHLY_TWEET_LIMIT - 100)).\
                    order_by(asc(KeyRateLimit.tweets_pulled)).\
                    limit(1).\
                    with_for_update(of=KeyRateLimit, nowait=True).one()
    keys.id = keys.id + 1
    keys.id = keys.id - 1
    print(f'{keys} T+{datetime.now()}', flush=True)
    keys2 = session.query(KeyRateLimit).\
                    where(and_(KeyRateLimit.type == twitter_api_token_type.archive,  KeyRateLimit.last_query < datetime.now() + timedelta(seconds=API_MANUAL_TIMEOUT), KeyRateLimit.tweets_pulled < API_MONTHLY_TWEET_LIMIT - 100)).\
                    order_by(asc(KeyRateLimit.tweets_pulled)).\
                    limit(1).\
                    with_for_update(of=KeyRateLimit, nowait=True).one()
    session.flush()
    print(f'{keys2} T+{datetime.now()}', flush=True)


    #docker-compose up | grep "initializer_1"