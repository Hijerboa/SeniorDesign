from machine_learning.keyword_extraction.get_keywords import get_keywords, get_subjects
from db.database_connection import initialize, create_session
from db.models import Bill, BillVersion
from datetime import datetime
from random import randint

def test_keyword_extraction():
    initialize()
    session = create_session()
    num = 10

    bills = session.query(Bill).offset(randint(0,10000)).limit(10).all()
    print('gotten bill')
    total_runtime = 0
    for bill in bills:
        # A handful of bills are screwy and don't have summaries
        
        if bill.summary == '':
            continue
        start = datetime.now()
        
        print('-------------------------------------------------------')

        print(f"\n{bill.title}")       

        
        print(get_keywords(bill))
        #print(get_subjects(bill))
        
        end = datetime.now()
        total_runtime += (end-start).total_seconds()
        input()
    average = total_runtime/num
    print(f"\nAverage Time: {average}")