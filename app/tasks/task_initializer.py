# Celery Initialization
# This file is what is called by the different Non-ML celery workers at startup
# It specfies what tasks will fall into what queues, as well celery settings
# At the end, it creates a database engine
from celery import Celery
from util.cred_handler import get_secret
from db.database_connection import initialize
from util.cred_handler import get_secret

BROKER_URL = f'amqp://{get_secret("RABBITMQ_USER")}:{get_secret("RABBITMQ_PASS")}@rabbit//'

# Specifies tasks routes
task_routes = {
    #Twitter
    'tasks.twitter_tasks.run_tweet_puller_archive': {'queue': 'twitter_archive'},
    'tasks.twitter_tasks.rerun_tweet_puller_archive': {'queue': 'twitter_archive'},
    'tasks.twitter_tasks.run_retrieve_user_info_by_id': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.rerun_retrieve_user_info_by_id': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.run_retrieve_user_info_by_username': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.rerun_retrieve_user_info_by_username': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.run_retrieve_users_info_by_ids': {'queue': 'twitter_users'},
    'tasks.twitter_tasks.rerun_retrieve_users_info_by_ids': {'queue': 'twitter_users'},
    #Propublica
    'tasks.propublica_tasks.get_bill_data_by_congress': {'queue': 'propublica'},
    'tasks.propublica_tasks.get_and_update_bill': {'queue': 'propublica'},
    'tasks.propublica_tasks.launch_bill_update': {'queue': 'propublica'},
    #Congress api
    'tasks.congress_api_tasks.get_versions': {'queue': 'propublica'}
}

# Creates celery object, using rabbit broker and database task backend
CELERY = Celery('tasks',
            broker=BROKER_URL,
            backend=get_secret('celery_connection_string'),
            include=['tasks.twitter_tasks', 'tasks.propublica_tasks', 'tasks.congress_api_tasks'])

# Celery settings, don't modify unless absolutely necessary
CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'json'
CELERY.conf.task_serializer = 'json'
CELERY.conf.task_routes = task_routes
CELERY.conf.task_track_started = True
CELERY.conf.task_acks_late = True
CELERY.conf.worker_prefetch_multiplier = 1
CELERY.conf.task_always_eager = False

# Create database engine
initialize()