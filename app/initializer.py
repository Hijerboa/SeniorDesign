import alembic.config
import os, os.path, time
from initializer.authentication_setup import perform_initial_tasks

from tasks.machine_learning_tasks import keyword_extraction_by_version

os.chdir(os.path.join(os.path.dirname(__file__), "db"))

time.sleep(3)

alembic.config.main(
    argv=[
        "--raiseerr",
        "upgrade",
        "head"
    ]
)

perform_initial_tasks()
"""time.sleep(5)
for i in range(0, 1):
    keyword_extraction_by_version.apply_async((i,))"""