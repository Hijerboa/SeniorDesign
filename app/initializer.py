import alembic.config
import os, os.path, time
from initializer.authentication_setup import perform_initial_tasks

os.chdir(os.path.join(os.path.dirname(__file__), "db"))

# Wait a second for db to be available, mainly used in a fully dockerized setup with a database in docker
time.sleep(1)

alembic.config.main(
    argv=[
        "--raiseerr",
        "upgrade",
        "head"
    ]
)

# Perform Auth setup
perform_initial_tasks()
