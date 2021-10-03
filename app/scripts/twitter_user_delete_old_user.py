from db.models import Tweet, TwitterUser
from db.database_connection import initialize, create_session


# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def do_things():
    initialize()
    session = create_session()
    author_ids = []
    for user in session.query(Tweet.author_id).distinct():
        author_ids.append(user['author_id'])
    print(len(author_ids))
    author_ids_not_detailed = []
    author_ids_detailed = []
    for user in session.query(TwitterUser.id).distinct():
        author_ids_detailed.append(user['id'])
    print(len(author_ids_detailed))
    for user_id in author_ids:
        if user_id not in author_ids_detailed:
            author_ids_not_detailed.append(user_id)
    print(len(author_ids_not_detailed))
    for user_id in author_ids_not_detailed:
        tweets = session.query(Tweet).filter(Tweet.author_id == str(user_id))
        for tweet in tweets:
            session.delete(tweet)
            session.commit()
