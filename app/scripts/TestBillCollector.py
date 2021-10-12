from apis.propublica_api import ProPublicaAPI
from util.cred_handler import get_secret
from db.models import Bill, BillSubject, CommitteeCodes, SubcommitteeCodes
from db.db_utils import get_or_create, get_single_object
from db.database_connection import initialize, create_session

def do_things():
    initialize()
    session = create_session()
    current_offset = 0
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))
    results = pro_publica_api.get_recent_bills(117, 'senate', 20)['data']['results'][0]['bills']
    for bill in results:
        co_sponsor_parties = bill['cosponsors_by_party']
        committee_codes = bill['committee_codes']
        subcommittee_codes = bill['subcommittee_codes']
        bad_items = ['sponsor_title', 'sponsor_name', 'sponsor_state', 'sponsor_uri', 'cosponsors_by_party', 'committee_codes', 'subcommittee_codes', 'bill_uri']
        for item in bad_items:
            bill.pop(item)
        if 'R' in co_sponsor_parties.keys():
            bill['rep_cosponsors'] = co_sponsor_parties['R']
        if 'D' in co_sponsor_parties.keys():
            bill['dem_cosponsors'] = co_sponsor_parties['D']
        bill['congress'] = 117
        object, created = get_or_create(session, Bill, bill_id=bill['bill_id'], defaults=bill)
        session.commit()
        for committee_code in committee_codes:
            committee_object, created = get_or_create(session, CommitteeCodes, committee_code=committee_code)
            session.commit()
            object.committee_codes.add(committee_object)
        for subcommittee_code in subcommittee_codes:
            subcommittee_object, created = get_or_create(session, SubcommitteeCodes, subcommittee_code=subcommittee_code)
            session.commit()
            object.sub_committee_codes.add(subcommittee_object)
        session.commit()


