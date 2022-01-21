import alembic.config
import os, os.path, time
from initializer.authentication_setup import perform_initial_tasks

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
