# Celery Initialization
from celery import Celery
from util.cred_handler import get_secret
from db.database_connection import initialize
from util.cred_handler import get_secret

BROKER_URL = 'amqp://{0}:{1}@rabbit//'.format(get_secret("RABBITMQ_USER"), get_secret("RABBITMQ_PASS"))

task_routes = {
    'tasks.machine_learning_tasks.keyword_extraction_by_bill': {'queue': 'ml_tasks'}
}

CELERY_ML = Celery('tasks',
            broker=BROKER_URL,
            backend=get_secret('celery_connection_string'),
            include=['tasks.machine_learning_tasks'])

CELERY_ML.conf.accept_content = ['json', 'msgpack']
CELERY_ML.conf.result_serializer = 'json'
CELERY_ML.conf.task_serializer = 'json'
CELERY_ML.conf.task_routes = task_routes
CELERY_ML.conf.task_track_started = True
CELERY_ML.conf.task_acks_late = True
CELERY_ML.conf.worker_prefetch_multiplier = 1
CELERY_ML.conf.worker_max_tasks_per_child = 1
CELERY_ML.conf.worker_max_memory_per_child = 120000

initialize()
