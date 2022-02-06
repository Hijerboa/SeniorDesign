from tasks.task_ml_initializer import CELERY_ML
from db.db_utils import get_single_object, get_or_create
from db.database_connection import create_session
from db.models import Bill, SearchPhrase, phrase_types
from machine_learning.keyword_extraction.get_keywords import get_keywords

@CELERY_ML.task()
def keyword_extraction_by_bill(id: str):
    session = create_session()
    bill_object: Bill = get_single_object(session, Bill, bill_id = id)
    try:
        sum_keywords, title_keywords = get_keywords(bill_object)
    # occcasionally you run into a one off error on the first few bills processed by a worker. This fixes it
    except AttributeError:
        sum_keywords, title_keywords = get_keywords(bill_object)
    for word in sum_keywords:
        object, created = get_or_create(session, SearchPhrase, search_phrase=word, type=phrase_types.summary)
        bill_object.keywords.append(object)
    for word in title_keywords:
        object, created = get_or_create(session, SearchPhrase, search_phrase=word, type=phrase_types.title)
        bill_object.keywords.append(object)
    session.commit()
    session.close()
    return None
    