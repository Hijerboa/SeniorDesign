from os import lseek

from db.models import Bill, SearchPhrase
from db.database_connection import initialize, create_session
from db.db_utils import get_or_create

def cleanup():
    initialize()
    session = create_session()
    bills = session.query(Bill).all()
    counter = 0
    for bill in bills:
        counter += 1
        print(bill.bill_id)
        for keyword in bill.keywords:
            bill.keywords.remove(keyword)
        session.commit()
    session.commit()