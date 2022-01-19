from tasks.task_ml_initializer import CELERY_ML
from db.db_utils import get_single_object, get_or_create
from db.database_connection import create_session
from db.models import BillVersion, Bill, BillKeyWord
from machine_learning.keyword_extraction.get_keywords import get_keywords

@CELERY_ML.task()
def keyword_extraction_by_bill(id: str):
    session = create_session()
    bill_object = get_single_object(session, Bill, bill_id = id)
    keywords = get_keywords(bill_object)
    for word in keywords:
        objects, created = get_or_create(session, BillKeyWord, bill=id, phrase=word)
    session.commit()
    session.close()
    