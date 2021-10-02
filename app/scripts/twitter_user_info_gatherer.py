from db.models import Tweet, TwitterUser
from db.database_connection import initialize, create_session
from util.cred_handler import get_secret
import requests

def do_things():
    initialize()
    session = create_session()

    for user in session.query(Tweet.author_id).distinct():
        requests.get("http://bunny.nicleary.com:5000/user_lookup?user={0}".format(str(user['author_id'])), headers= {
            'Authorization': 'Bearer {0}'.format(get_secret("bunny_server_api_key"))
        })
