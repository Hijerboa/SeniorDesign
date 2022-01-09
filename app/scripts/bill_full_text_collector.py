from util.cred_handler import get_secret
from apis.govinfo_api import GovInfoAPI, GovInfoAPIError
from db.models import Bill, BillAction, BillVersion, CommitteeCodes, SubcommitteeCodes
from db.db_utils import get_or_create, create_single_object
from db.database_connection import initialize, create_session
from html.parser import HTMLParser
import pymysql
import time
pymysql.install_as_MySQLdb()

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.current_is_pre = True

    def handle_endtag(self, tag):
        if tag == "pre":
            self.current_is_pre = False

    def handle_data(self, data):
        if self.current_is_pre:
            self.important_data = data

    def run_feeder(self, input):
        self.feed(input)
        return self.important_data


def collect_full_text():
    num_bill = 0

    gov_api: GovInfoAPI = GovInfoAPI(get_secret('gov_info_url'), get_secret('gov_info_key'))

    initialize()
    session = create_session()
    bills: [Bill] = session.query(Bill).order_by(Bill.congress.desc()).filter(Bill.congress == 117).offset(0).all()
    print(len(bills))
    for bill in bills:
        num_bill += 1
        if not len(bill.versions) == 0:
            version_num = 0
            for version in bill.versions:
                try:
                    version_len = len(bill.versions)
                    version_num += 1
                    string = 'BILLS-{0}{1}{2}'.format(str(bill.congress), bill.bill_slug, version.title.lower())
                    response = gov_api.get_bill_full_text(string)
                    parser = MyHTMLParser()
                    result = parser.run_feeder(response['data'].decode())
                    version.full_text = result
                    session.commit()
                    print('Collection full text for bill {0}/{1}, version {2}/{3}'.format(str(num_bill), str(len(bills)), str(version_num), str(version_len)))
                except GovInfoAPIError:
                    continue
    session.close()