from cProfile import run
import alembic.config
import os, os.path, time
from initializer.authentication_setup import perform_initial_tasks
from tasks.bill_request_tasks import run_process_bill_request

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
#ex()

"""from db.database_connection import create_session
from db.models import Bill
from tasks.machine_learning_tasks import keyword_extraction_by_bill

session = create_session()
bills: [Bill] = session.query(Bill).filter(Bill.keywords == None).all()
for bill in bills:
    keyword_extraction_by_bill.apply_async((bill.bill_id,))"""

from db.database_connection import create_session
from db.models import Bill
from tasks.bill_request_tasks import run_process_bill_request

offset = 1000
con = True
while con:
    session = create_session()
    bills: [Bill] = session.query(Bill).offset(offset).limit(10).all()
    if not len(bills) == 10:
        con = False
    for bill in bills:
        run_process_bill_request(bill.bill_id, 1)
    offset += 10
    session.close()
