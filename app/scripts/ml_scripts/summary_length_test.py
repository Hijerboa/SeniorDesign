from db.models import Bill
from db.database_connection import initialize, create_session

def test_bill_summary_length():
    initialize()
    session = create_session()
    bills = session.query(Bill).all()
    under_1000 = 0
    under_10000 = 0
    under_100000 = 0
    over_100000 = 0
    for bill in bills:
        if bill.summary is None:
            continue
        if len(bill.summary) > 100000:
            over_100000 += 1
        elif len(bill.summary) > 10000:
            under_100000 += 1
        elif len(bill.summary) > 1000:
            under_10000 += 1
        else:
            under_1000 += 1
    print(f'{under_1000} with a length under 1000')
    print(f'{under_10000} with a length between 1000 and 10000')
    print(f'{under_100000} with a length between 10000 and 100000')
    print(f'{over_100000} with a length over 100000')
            