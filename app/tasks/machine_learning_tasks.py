from tasks import CELERY
from db.db_utils import get_single_object, get_or_create
from db.database_connection import create_session
from db.models import BillVersion, Bill, BillKeyWord
from machine_learning.keyword_extraction.get_keywords import get_keywords

@CELERY.task()
def keyword_extraction_by_version(bill_version_id: int):
    session = create_session()
    bill_version_object: BillVersion = get_single_object(session, BillVersion, id=bill_version_id)
    bill_id = bill_version_object.bill
    bill_object = get_single_object(session, Bill, bill_id=bill_id)
    summary = bill_object.summary.replace("\n", '')
    full_text = bill_version_object.full_text.replace("\n", '')
    keywords = get_keywords(summary, full_text)
    for word in keywords:
        object, created = get_or_create(session, BillKeyWord, bill=bill_id, phrase=word)
    session.commit()
    session.close()
    