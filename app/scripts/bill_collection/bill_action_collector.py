from util.cred_handler import get_secret
from apis.propublica_api import ProPublicaAPI, PropublicaAPIError
from db.models import Bill, BillAction, BillVersion
from db.db_utils import get_or_create, create_single_object
from db.database_connection import initialize, create_session
import pymysql
import time
pymysql.install_as_MySQLdb()


def bill_action_collector():
    api: ProPublicaAPI = ProPublicaAPI(get_secret('pro_publica_url'), get_secret('pro_publica_api_key'))
    initialize()
    session = create_session()
    offset = 0
    number = offset
    bills: [Bill] = session.query(Bill).order_by(Bill.congress.desc()).filter(Bill.congress == 117).all()
    print("Collected bills")
    no_action_version = []
    num = 0
    """for bill in bills:
        if number >= (offset + 4950):
            break
        number +=1
        print('Congress: {0}. Slug: {1} Number: {2}'.format(str(bill.congress), str(bill.bill_slug), str(number)))
        try:
            result = api.get_bill_activity(bill.bill_slug, bill.congress)
            if result['data']['results'][0]['versions'] is not None:
                for version in result['data']['results'][0]['versions']:
                    version['bill'] = bill.bill_id
                    instance, created = get_or_create(session, BillVersion, bill=version['bill'], congressdotgov_url=version['congressdotgov_url'], defaults=version)
                    session.commit()
            if result['data']['results'][0]['actions'] is not None:
                for action in result['data']['results'][0]['actions']:
                    action['order'] = action['id']
                    action.pop('id')
                    action['bill'] = bill.bill_id
                    instance, created = get_or_create(session, BillAction, bill=action['bill'], order=action['order'], defaults=action)
                    session.commit()
        except PropublicaAPIError:
            time.sleep(600)
            pass
        time.sleep(0.3)"""
    for bill in bills:
        if len(bill.versions) == 0:
            no_action_version.append(bill)
    print("Gathered all bills that are sad :(")
    number = 0
    for bill in no_action_version:
        number += 1
        print('Congress: {0}. Slug: {1} Number: {2}/{3}'.format(str(bill.congress), str(bill.bill_slug), str(number), str(len(no_action_version))))
        try:
            result = api.get_bill_activity(bill.bill_slug, bill.congress)
            if result['data']['results'][0]['versions'] is not None:
                for version in result['data']['results'][0]['versions']:
                    version['bill'] = bill.bill_id
                    instance, created = get_or_create(session, BillVersion, bill=version['bill'], congressdotgov_url=version['congressdotgov_url'], defaults=version)
                    session.commit()
            if result['data']['results'][0]['actions'] is not None:
                for action in result['data']['results'][0]['actions']:
                    action['order'] = action['id']
                    action.pop('id')
                    action['bill'] = bill.bill_id
                    instance, created = get_or_create(session, BillAction, bill=action['bill'], order=action['order'], defaults=action)
                    session.commit()
        except PropublicaAPIError:
            time.sleep(600)
            pass
