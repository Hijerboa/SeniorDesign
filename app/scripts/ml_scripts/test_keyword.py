from machine_learning.keyword_extraction.get_keywords import get_keywords, get_subjects
from db.database_connection import initialize, create_session
from db.models import Bill, BillVersion
from datetime import datetime
from random import randint

def test_keyword_extraction():
    initialize()
    session = create_session()
    num = 50
    batches = 20
    total_runtime = 0

    for c_batch in range(batches):
        bills = session.query(Bill).offset(num * c_batch).limit(num).all()
        print(f'retreived bills {num * c_batch} - {num * (c_batch + 1) - 1}')
        sec_runtime = 0
        for bill in bills:
            # A handful of bills are screwy and don't have summaries
            
            if bill.summary == '':
                continue

            
            print('-------------------------------------------------------')

            print(f"\n{bill.title}\n")    
            print(f"{bill.summary}\n")   
            start = datetime.now()
            
            kw = get_keywords(bill)
            
            end = datetime.now()
            print(kw)
            sec_runtime += (end-start).total_seconds()
            total_runtime += (end-start).total_seconds()
            input()
        print(f'{(c_batch + 1) * num} / {batches * num} done (avg: {sec_runtime / num} s.)')
    average = total_runtime/(num * batches)
    print(f"\nAverage Time: {average}")