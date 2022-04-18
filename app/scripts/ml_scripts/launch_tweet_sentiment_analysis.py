from asyncio import tasks
from mimetypes import init
from db.database_connection import initialize, create_session
from db.models import Tweet, UnprocessedTweet
from tasks.machine_learning_tasks import run_get_tweet_sentiments

def chunks(input_list, length):
    length = max(1, length)
    return (input_list[i:i + length] for i in range(0, len(input_list), length))

def launch_tweet_sentiment_analysis():
    initialize()
    
    session = create_session()
    
    unprocessed_objects = session.query(UnprocessedTweet).all()
    
    for chunk in chunks(unprocessed_objects, 100):
        print('chunk')
        tweet_ids = []
        un_done_ids = []
        for item in chunk:
            tweet_ids.append(str(item.tweet_id))
            un_done_ids.append(item.id)
        run_get_tweet_sentiments.apply_async((tweet_ids, 1,))
        # for id in un_done_ids:
        #     session.query(UnprocessedTweet).filter(UnprocessedTweet.id==id).delete()
            
    session.close()