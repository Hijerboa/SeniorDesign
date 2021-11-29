from util.cred_handler import get_secret
from apis.propublica_api import ProPublicaAPI, PropublicaAPIError
from db.models import Bill, BillAction, BillVersion, CommitteeCodes, SubcommitteeCodes
from db.db_utils import get_or_create, create_single_object
from db.database_connection import initialize, create_session
import pymysql
import time
pymysql.install_as_MySQLdb()

congress_id = 113
congress_chamber = 'house'

initialize()

def do_things():

    session = create_session()
    num_bills = 0
    current_offset = 4860
    valid_results = True
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))

    while valid_results:
        results = pro_publica_api.get_recent_bills(congress_id, congress_chamber, current_offset)
        if results['data']['results'][0]['num_results'] == 0:
            valid_results = False
            break
        bills = results['data']['results'][0]['bills']
        for bill in bills:
            co_sponsor_parties = bill['cosponsors_by_party']
            committee_codes = bill['committee_codes']
            subcommittee_codes = bill['subcommittee_codes']
            bad_items = ['sponsor_title', 'sponsor_name', 'sponsor_state', 'sponsor_uri', 'cosponsors_by_party',
                         'committee_codes', 'subcommittee_codes', 'bill_uri']
            for item in bad_items:
                bill.pop(item)
            if 'R' in co_sponsor_parties.keys():
                bill['rep_cosponsors'] = co_sponsor_parties['R']
            if 'D' in co_sponsor_parties.keys():
                bill['dem_cosponsors'] = co_sponsor_parties['D']
            bill['congress'] = congress_id
            object, created = get_or_create(session, Bill, bill_id=bill['bill_id'], defaults=bill)
            num_bills += 1
            print(num_bills + current_offset)
            session.commit()
            for committee_code in committee_codes:
                committee_object, created = get_or_create(session, CommitteeCodes, committee_code=committee_code)
                session.commit()
                object.committee_codes.append(committee_object)
            for subcommittee_code in subcommittee_codes:
                subcommittee_object, created = get_or_create(session, SubcommitteeCodes,
                                                             subcommittee_code=subcommittee_code)
                session.commit()
                object.sub_committee_codes.append(subcommittee_object)
        current_offset += 20
        session.commit()
    session.commit()
    session.close()