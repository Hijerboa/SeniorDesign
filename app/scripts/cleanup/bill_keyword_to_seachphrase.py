from os import lseek

from db.models import Bill, BillKeyWord, SearchPhrase
from db.database_connection import initialize, create_session
from db.db_utils import get_or_create

def migrate_keyword_to_search_phrase():
    initialize()
    session = create_session()
    bills = session.query(Bill).offset(10).all()
    for bill in bills:
        print(bill.bill_id)
        keywords = session.query(BillKeyWord).filter(BillKeyWord.bill == bill.bill_id).all()
        for keyword in keywords:
            search_object, created = get_or_create(session, SearchPhrase, search_phrase=keyword.phrase)
            bill.keywords.append(search_object)
        session.commit()