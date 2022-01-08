# Celery Initialization
from celery import Celery, current_task, uuid
from celery.exceptions import CeleryError
from celery.result import AsyncResult
from util.cred_handler import get_secret
from db.database_connection import initialize
from db.db_utils import get_or_create, get_single_object
from db.models import Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, User
from twitter_utils.user_gatherer import create_user_object

BROKER_URL = 'amqp://{0}:{1}@rabbit//'.format(get_secret("RABBITMQ_USER"), get_secret("RABBITMQ_PASS"))

task_routes = {
    'tasks.twitter_tasks.tweet_puller_stream': {'queue': 'twitter_stream'},
    'tasks.twitter_tasks.tweet_puller_archive': {'queue': 'twitter_archive'},
    'tasks.twitter_tasks.retrieve_user_info_by_id': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.retrieve_user_info_by_username': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.retrieve_users_info_by_ids': {'queue': 'twitter_users'},
    'tasks.propublica_tasks.get_bill_data_by_congress': {'queue': 'propublica_tasks'},
    'tasks.machine_learning_tasks.keyword_extraction_by_version': {'queue': 'ml_tasks'}
}

CELERY = Celery('tasks',
            broker=BROKER_URL,
            include=['tasks.twitter_tasks', 'tasks.propublica_tasks', 'tasks.congress_api_tasks', 'tasks.machine_learning_tasks'])

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'json'
CELERY.conf.task_serializer = 'json'
CELERY.conf.task_routes = task_routes
CELERY.conf.task_track_started = True
CELERY.conf.acks_late = True
CELERY.conf.preftch_multiplier = 1

initialize()