celery -A tasks.task_ml_initializer worker -l INFO -Q ml_tasks --concurrency 1 --pool threads --without-gossip --without-mingle
