from util.cred_handler import get_secret
from apis.govinfo_api import GovInfoAPI, GovInfoAPIError
from db.models import Bill, BillAction, BillVersion, CommitteeCodes, SubcommitteeCodes
from db.db_utils import get_or_create, create_single_object
from db.database_connection import initialize, create_session
from html.parser import HTMLParser
import pymysql
import time
pymysql.install_as_MySQLdb()


def collect_without_version():
    num_bill = 0

    gov_api: GovInfoAPI = GovInfoAPI(get_secret('gov_info_url'), get_secret('gov_info_key'))

    initialize()
    session = create_session()
    bills: [Bill] = session.query(Bill).order_by(Bill.congress.desc()).filter(Bill.congress == 117).offset(0).all()
    without = 0
    for bill in bills:
        num_bill += 1
        if len(bill.versions) == 0:
            without += 1
            print(bill.bill_id)
    print("{0}/{1}".format(str(without), str(len(bills))))
    session.close()