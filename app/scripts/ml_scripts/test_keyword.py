from typing_extensions import runtime
from machine_learning.keyword_extraction.get_keywords import get_keywords
from db.database_connection import initialize, create_session
from db.models import Bill, BillVersion
from db.db_utils import get_single_object
from datetime import datetime

def do_things():
    initialize()
    session = create_session()
    num = 1000
    bills = session.query(Bill).offset(3).limit(num).all()
    total_runtime = 0
    for bill in bills:
        start = datetime.now()
        print(get_keywords(bill.summary.replace('\n', ''), ''))
        end = datetime.now()
        total_runtime += (end-start).total_seconds()
    average = total_runtime/num
    print(average)