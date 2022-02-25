# Celery ML Initialization
# This file is what is called by ML celery workers at startup.
# This is split out from the general initializer, as the ML workers need root access
# It specfies what tasks will fall into what queues, as well celery settings
# At the end, it creates a database engine
from celery import Celery
from util.cred_handler import get_secret
from db.database_connection import initialize
from util.cred_handler import get_secret

BROKER_URL = f'amqp://{get_secret("RABBITMQ_USER")}:{get_secret("RABBITMQ_PASS")}@{get_secret("RABBITMQ_HOST")}//'

# Specifies task routes
task_routes = {
    'tasks.machine_learning_tasks.keyword_extraction_by_bill': {'queue': 'ml_tasks'}
}

# Creates celery object, using rabbit broker and database task backend
CELERY_ML = Celery('tasks',
            broker=BROKER_URL,
            backend=get_secret('celery_connection_string'),
            include=['tasks.machine_learning_tasks'])

# Celery settings, don't modify unless absolutely necessary
CELERY_ML.conf.accept_content = ['json', 'msgpack']
CELERY_ML.conf.result_serializer = 'json'
CELERY_ML.conf.task_serializer = 'json'
CELERY_ML.conf.task_routes = task_routes
CELERY_ML.conf.task_track_started = True
CELERY_ML.conf.task_acks_late = True
CELERY_ML.conf.worker_prefetch_multiplier = 1
CELERY_ML.conf.worker_max_tasks_per_child = 1
CELERY_ML.conf.worker_max_memory_per_child = 120000

# Create database engine
initialize()
