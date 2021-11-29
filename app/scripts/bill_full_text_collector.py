from util.cred_handler import get_secret
from apis.govinfo_api import GovInfoAPI
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


def do_things():

    gov_api: GovInfoAPI = GovInfoAPI(get_secret('gov_info_url'), get_secret('gov_info_key'))

    initialize()
    session = create_session()
    bills: [Bill] = session.query(Bill).order_by(Bill.congress.desc()).offset(0).limit(100).all()
    """response = gov_api.get_bill_full_text('BILLS-117hr5985ih')
    string = response['data'].decode()
    parser = MyHTMLParser()
    parser.feed(string)"""
    big_string = ""
    for bill in bills:
        if not len(bill.versions) == 0:
            for version in bill.versions:
                string = 'BILLS-{0}{1}{2}'.format(str(bill.congress), bill.bill_slug, version.title.lower())
                response = gov_api.get_bill_full_text(string)
                parser = MyHTMLParser()
                #parser.feed(response['data'].decode())
                result = parser.run_feeder(response['data'].decode())
                big_string += result
    print(len(big_string))