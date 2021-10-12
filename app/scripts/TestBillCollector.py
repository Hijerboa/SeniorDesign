from apis.propublica_api import ProPublicaAPI
from util.cred_handler import get_secret

def do_things():
    current_offset = 0
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))
    results = pro_publica_api.get_recent_bills(117, 'senate', 20)['data']['results'][0]['bills']
    for bill in results:
        print(bill['bill_id'])