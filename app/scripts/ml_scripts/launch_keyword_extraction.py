from db.models import Bill
from db.database_connection import initialize, create_session
from util.cred_handler import get_secret
import sys, time, requests


# A script to make requests to the API server to launch the keyword extraction
def launch_keyword_extraction():
    initialize()
    session = create_session()
    bills = session.query(Bill).limit(2500+4470 + 4000).all()
    num = 0
    for bill in bills:
        num += 1
        requests.get(f'http://bunny.nicleary.com:5000/ml_tasks/bill_keywords?bill_id={bill.bill_id}', headers={
                'Authorization': 'Bearer {0}'.format(get_secret("bunny_server_api_key"))
            })
        sys.stdout.write(f'\r{num} bills requested')
        sys.stdout.flush()
    sys.stdout.write('\n')