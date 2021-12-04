from util.cred_handler import get_secret
from apis.govinfo_api import GovInfoAPI, GovInfoAPIError
from db.models import Bill, BillAction, BillVersion
from db.db_utils import get_or_create, create_single_object
from db.database_connection import initialize, create_session
import pymysql
from util.bill_regex import SplitBillSlug
import time
pymysql.install_as_MySQLdb()


def do_things():
    initialize()
    api: GovInfoAPI = GovInfoAPI(get_secret('gov_info_url'), get_secret('gov_info_key'))
    start_string = '1999-01-01T00:00:00Z'
    end_date = '2021-12-12T00:00:00Z'
    offset = 0
    while True:
        response = api.get_bill_listing(start_string, end_date, offset)
        packages = response['data']['packages']
        for package in packages:
            session = create_session()
            summary_response = api.get_bill_summary(package['packageId'])['data']
            bill_slug = str(summary_response['billType']) + str(summary_response['billNumber'])
            bill_id = '{0}-{1}'.format(bill_slug, str(summary_response['congress']))
            item, created = get_or_create(session, Bill, bill_slug=bill_slug, bill_id=bill_id,
                                          congress=int(summary_response['congress']), title=summary_response['title'])
            session.commit()
            print(created)
            time.sleep(1)
        offset += 100