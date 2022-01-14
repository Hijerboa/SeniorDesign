from machine_learning.keyword_extraction.get_keywords import get_keywords
from db.database_connection import initialize, create_session
from db.models import Bill, BillVersion
from datetime import datetime

def test_keyword_extraction():
    initialize()
    session = create_session()
    num = 10
    bills = session.query(Bill).offset(1010).limit(num).all()
    total_runtime = 0
    for bill in bills:
        # A handful of bills are screwy and don't have summaries
        if bill.summary == '':
            continue
        start = datetime.now()
        print(f"\n{bill.title}")
        print(bill.number)
        print(get_keywords(bill))
        end = datetime.now()
        total_runtime += (end-start).total_seconds()
    average = total_runtime/num
    print(f"\nAverage Time: {average}")