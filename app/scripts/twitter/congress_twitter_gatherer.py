from db.models import Tweet, TwitterUser, CongressMemberData
from db.database_connection import initialize, create_session
from util.cred_handler import get_secret
import requests


def gather_congress_twitter():
    initialize()
    session = create_session()
    all_congress = session.query(CongressMemberData).all()
    cong_with_twitter = []
    for member in all_congress:
        if not member.twitter_account is None:
            response = requests.get(
                "http://bunny.nicleary.com:5000/twitter/users/lookup/by_username/single?username={0}".format(str(member.twitter_account)),
                headers={
                    'Authorization': 'Bearer {0}'.format(get_secret("bunny_server_api_key"))
                })
            print(response.json())
