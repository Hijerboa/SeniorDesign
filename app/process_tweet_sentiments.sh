celery -A tasks.task_ml_initializer worker -l INFO -Q ml_tasks --concurrency 2 --pool threads --without-gossip --without-mingle
