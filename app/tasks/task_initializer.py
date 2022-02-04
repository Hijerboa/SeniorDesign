# Celery Initialization
from celery import Celery
from util.cred_handler import get_secret
from db.database_connection import initialize
from util.cred_handler import get_secret

BROKER_URL = 'amqp://{0}:{1}@rabbit//'.format(get_secret("RABBITMQ_USER"), get_secret("RABBITMQ_PASS"))

task_routes = {
    'tasks.twitter_tasks.tweet_puller_archive': {'queue': 'twitter_archive'},
    'tasks.twitter_tasks.retrieve_user_info_by_id': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.retrieve_user_info_by_username': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.retrieve_users_info_by_ids': {'queue': 'twitter_users'},
    'tasks.propublica_tasks.get_bill_data_by_congress': {'queue': 'propublica'},
    'tasks.propublica_tasks.get_and_update_bill': {'queue': 'propublica'},
    'tasks.propublica_tasks.launch_bill_update': {'queue': 'propublica'},
    'tasks.congress_api_tasks.get_versions': {'queue': 'propublica'}
}

CELERY = Celery('tasks',
            broker=BROKER_URL,
            backend=get_secret('celery_connection_string'),
            include=['tasks.twitter_tasks', 'tasks.propublica_tasks', 'tasks.congress_api_tasks'])

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'json'
CELERY.conf.task_serializer = 'json'
CELERY.conf.task_routes = task_routes
CELERY.conf.task_track_started = True
CELERY.conf.task_acks_late = True
CELERY.conf.worker_prefetch_multiplier = 1
CELERY.conf.task_always_eager = False

initialize()