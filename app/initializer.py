import alembic.config
import os, os.path, time
from initializer.authentication_setup import perform_initial_tasks
from tasks.bill_request_tasks import run_process_bill_request
from runner_example import ex

import logging
logger = logging.getLogger(__name__)

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
print("startup tasks complete")
#run_process_bill_request.apply(('hconres108-112', 1,))
ex()
