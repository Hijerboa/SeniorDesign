from util.cred_handler import get_secret
from db.models import CongressMemberData
from db.database_connection import initialize, create_session
import pymysql
from sqlalchemy import null
import requests

pymysql.install_as_MySQLdb()


def do_things():
    initialize()
    session = create_session()
    members: [CongressMemberData] = session.query(CongressMemberData).filter(
        CongressMemberData.twitter_account != null()).all()
    for member in members:
        args = {
            'query': 'from:{0}'.format(member.twitter_account),
            'start': '2007-01-01',
            'end': '2021-12-07'
        }
        response = requests.get('http://bunny.nicleary.com:5000/twitter/tweets/archive/search', params=args, headers={
            'Authorization': 'Bearer {0}'.format(get_secret('bunny_server_api_key'))
        })
        print(member.twitter_account)
