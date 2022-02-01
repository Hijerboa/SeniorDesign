from tasks.task_initializer import CELERY

import time
import datetime
from util.cred_handler import get_secret
from apis.propublica_api import ProPublicaAPI
from db.database_connection import create_session
from db.db_utils import get_or_create, get_single_object
from db.models import Bill, CommitteeCodes, SubcommitteeCodes, BillAction, BillVersion


@CELERY.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Launch tasks once a day
    sender.add_periodic_task(86400.0, launch_bill_update.s(117), name='Periodic action and version collection')
    sender.add_periodic_task(86400.0, get_bill_data_by_congress.s(117, 'both'), name='Periodic bill collection')
    

@CELERY.task()
def launch_bill_update(congress_number: int):
    session = create_session()
    bills = session.query(Bill).filter(Bill.active==True, Bill.congress==congress_number)
    for bill in bills:
        get_and_update_bill.apply_async((bill.bill_id,))


@CELERY.task()
def get_bill_data_by_congress(congress_id: int, congress_chamber: str):
    session = create_session()
    num_bills = 0
    current_offset = 0
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
            if created:
                get_and_update_bill.apply_async((object.bill_id,))
            num_bills += 1
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
    return '{0} bills collected'.format(str(num_bills))


@CELERY.task()
def get_and_update_bill(bill_id: str):
    session = create_session()
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))
    bill: Bill = get_single_object(session, Bill, bill_id=bill_id)
    bill_response = pro_publica_api.get_bill_activity(bill.bill_slug, bill.congress)
    bill_instance = bill_response['data']['results'][0]
    # Update bill attributes
    bill.active = bill_instance['active']
    bill.last_vote = bill_instance['last_vote']
    bill.house_passage = bill_instance['house_passage']
    bill.senate_passage = bill_instance['senate_passage']
    bill.latest_major_action_date = bill_instance['latest_major_action_date']
    bill.latest_major_action = bill_instance['latest_major_action']
    bill.summary = bill_instance['summary']
    bill.summary_short = bill_instance['summary_short']
    session.commit()
    
    if bill_instance['versions'] is not None:
        for version in bill_instance['versions']:
            version['bill'] = bill.bill_id
            instance, created = get_or_create(session, BillVersion, bill=version['bill'], congressdotgov_url=version['congressdotgov_url'], defaults=version)
            session.commit()
    if bill_instance['actions'] is not None:
        for action in bill_instance['actions']:
            action['order'] = action['id']
            action.pop('id')
            action['bill'] = bill.bill_id
            instance, created = get_or_create(session, BillAction, bill=action['bill'], order=action['order'], defaults=action)
            session.commit()
    session.close()
    return None
    