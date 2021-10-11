from db.models import Tweet, TwitterUser
from db.database_connection import initialize, create_session
from util.cred_handler import get_secret
import requests


# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def do_things():
    initialize()
    session = create_session()

    """for user in session.query(Tweet.author_id).distinct():
        
        requests.get("http://bunny.nicleary.com:5000/user_lookup?user={0}".format(str(user['author_id'])), headers= {
            'Authorization': 'Bearer {0}'.format(get_secret("bunny_server_api_key"))
        })
    """
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
    arrays = divide_chunks(author_ids_not_detailed, 100)
    for array in arrays:
        string = ','.join(array)
        #print(string)
        response = requests.get("http://bunny.nicleary.com:5000/twitter/users/lookup/by_id/multiple?users={0}".format(str(string)), headers={
            'Authorization': 'Bearer {0}'.format(get_secret("bunny_server_api_key"))
        })
        print(response)
