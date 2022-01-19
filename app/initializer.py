import alembic.config
import os, os.path, time
from initializer.authentication_setup import perform_initial_tasks
from db.database_connection import create_session
from db.models import Bill

from tasks.machine_learning_tasks import keyword_extraction_by_bill

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
"""time.sleep(2)
session = create_session()
bills = session.query(Bill).offset(10).limit(100).all()
for bill in bills:
    keyword_extraction_by_bill.apply_async((bill.bill_id,))
session.close()"""