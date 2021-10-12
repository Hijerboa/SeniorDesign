from db.models import CongressMemberData
from db.database_connection import initialize, create_session
import requests
from util.cred_handler import get_secret

def do_things():
    initialize()
    session = create_session()

    congress_members_twitter_account = session.query(CongressMemberData.twitter_account).filter(CongressMemberData.twitter_account is not None)
    for account in congress_members_twitter_account:
        if account['twitter_account'] is not None and not account['twitter_account'] == "None":
            requests.get("http://bunny.nicleary.com:5000/users/lookup/by_username/single?username={0}".format(str(account['twitter_account'])), headers={
                'Authorization': 'Bearer {0}'.format(get_secret("bunny_server_api_key"))
            })
            print("{0} looked up".format(account['twitter_account']))

