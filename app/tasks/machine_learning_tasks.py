from venv import create
from db.db_utils import create_single_object
from tasks.task_ml_initializer import CELERY_ML
from db.db_utils import get_single_object, get_or_create
from db.database_connection import create_session
from db.models import Bill, SearchPhrase, phrase_types, Task, TaskError, Tweet
from machine_learning.keyword_extraction.get_keywords import get_keywords
from machine_learning.sentiment_analysis.tweet_sentiment_analysis import score_batch

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


@CELERY_ML.task()
def run_get_tweet_sentiments(tweet_ids, user_id):
    session = create_session(expire_on_commit=False)
    task = get_tweet_sentiments(tweet_ids, user_id)
    session.add(task)
    session.commit()
    session.close()
    res = task.run()
    return res
    
    
class get_tweet_sentiments(Task):
    def __init__(self, tweet_ids, user_id):
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='get_tweet_sentiments', parameters={'tweet_ids': tweet_ids})
        
    def run(self):
        try:
            session = create_session()
            tweet_ids = [str(tweet_id) for tweet_id in self.parameters['tweet_ids']]
            tweet_objects = session.query(Tweet).filter(Tweet.id.in_(tweet_ids)).all()
            list = []
            for object in tweet_objects:
                list.append((str(object.id), object.text))
            scored = score_batch(list)
            for scored_tweet in scored:
                session.query(Tweet).filter(Tweet.id==scored_tweet[0]).update({'sentiment': scored_tweet[1], 'sentiment_confidence': scored_tweet[2]})
            session.commit()
            session.close()
            return f'Scored {len(tweet_ids)} tweets'
        except Exception as e:
            session = create_session()
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            session.commit()
            session.close()
            return str(e)
