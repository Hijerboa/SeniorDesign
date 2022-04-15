<<<<<<< HEAD
celery -A tasks.task_ml_initializer worker -l INFO -Q ml_tasks --concurrency 1 --pool threads --without-gossip --without-mingle
=======
celery -A tasks.task_ml_initializer worker -l INFO -Q ml_tasks --concurrency 2 --pool threads --without-gossip --without-mingle
>>>>>>> 138b8066dbfbb9ac20d673825fbb76c1c9bdf8f0
