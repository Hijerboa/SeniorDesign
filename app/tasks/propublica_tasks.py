from tasks.task_initializer import CELERY
from util.cred_handler import get_secret
from apis.propublica_api import ProPublicaAPI, PropublicaAPIError
from db.database_connection import create_session
from db.db_utils import create_single_object, get_or_create, get_single_object
from db.models import Bill, CommitteeCodes, SubcommitteeCodes, BillAction, BillVersion, Task, TaskError


@CELERY.task()
def get_bill_data_by_congress(task_id: int):
    """Gets bill data for all bills in a specified congress and chamber

    Args:
        task_id (int): Integer ID of a task object. This is pulled to get info about task parameters
    """
    session = create_session()
    task_object: Task = get_single_object(session, Task, id=task_id)
    num_bills = 0
    current_offset = 0
    valid_results = True
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))
    # Run through this for every single bill for the specified congress and chamber, potentially thousands
    while valid_results:
        try:
            results = pro_publica_api.get_recent_bills(task_object.parameters['congress'], task_object.parameters['chamber'], current_offset)
        except PropublicaAPIError as e:
            create_single_object(session, TaskError, task_id=task_object.id, description=e)
            task_object.error = True
            session.commit()
            session.close()
            return
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
            # Items we don't store in the DB. Remove them from the dict
            for item in bad_items:
                bill.pop(item)
            if 'R' in co_sponsor_parties.keys():
                bill['rep_cosponsors'] = co_sponsor_parties['R']
            if 'D' in co_sponsor_parties.keys():
                bill['dem_cosponsors'] = co_sponsor_parties['D']
            bill['congress'] = task_object.parameters['congress']
            object, created = get_or_create(session, Bill, bill_id=bill['bill_id'], defaults=bill)
            session.commit()
            # If created, then pull versions and actions
            if created:
                new_task: Task = create_single_object(session, Task, defaults={'launched_by_id': task_object.launched_by_id, 'type': 'propublica_update_bill', 'parameters': {
                    'bill_id': object.bill_id
                }})
                session.commit()
                get_and_update_bill.apply_async((new_task.id,))
            num_bills += 1
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
    task_object.complete = True
    session.commit()
    session.close()
    return '{0} bills collected'.format(str(num_bills))


@CELERY.task()
def get_and_update_bill(task_id):
    """ Retrieves updated bill information about a bill, including new actions and versions

    Args:
        task_id ([type]): Integer representation of a task object
    """
    session = create_session()
    pro_publica_api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))
    task_object: Task = get_single_object(session, Task, id=task_id)
    bill_id = task_object.parameters['bill_id']
    bill: Bill = get_single_object(session, Bill, bill_id=bill_id)
    try:
        bill_response = pro_publica_api.get_bill_activity(bill.bill_slug, bill.congress)
    except PropublicaAPIError as e:
            create_single_object(session, TaskError, task_id=task_object.id, description=e)
            task_object.error = True
            session.commit()
            session.close()
            return
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

    # Add any new versions to the database
    if bill_instance['versions'] is not None:
        for version in bill_instance['versions']:
            version['bill'] = bill.bill_id
            instance, created = get_or_create(session, BillVersion, bill=version['bill'],
                                              congressdotgov_url=version['congressdotgov_url'], defaults=version)
            session.commit()
    
    # Add any new actions to the database
    if bill_instance['actions'] is not None:
        for action in bill_instance['actions']:
            action['order'] = action['id']
            action.pop('id')
            action['bill'] = bill.bill_id
            instance, created = get_or_create(session, BillAction, bill=action['bill'], order=action['order'],
                                              defaults=action)
            session.commit()
    task_object.complete = True
    session.commit()
    session.close()
    return None
