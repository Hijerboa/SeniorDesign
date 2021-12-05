from util.cred_handler import get_secret
from apis.govinfo_api import GovInfoAPI, GovInfoAPIError
from db.models import Bill, BillAction, BillVersion
from db.db_utils import get_or_create, create_single_object
from db.database_connection import initialize, create_session
import pymysql
from html.parser import HTMLParser
from util.bill_regex import SplitBillSlug
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


def do_things(congress: int, version, doc_class):
    initialize()
    api: GovInfoAPI = GovInfoAPI(get_secret('gov_info_url'), get_secret('gov_info_key'))
    start_string = '1999-01-01T00:00:00Z'
    end_date = '2021-12-12T00:00:00Z'
    offset = 0
    num_items_processed = 0
    num_bills_created = 0
    num_versions_created = 0
    num_full_text_pulled = 0
    print('Processing Data for Congress #{0}, Version type {1}, doc class {2}'.format(str(congress), version, doc_class))
    while True:
        response = api.get_bill_listing(start_string, end_date, offset, congress, version, doc_class)
        packages = response['data']['packages']
        if len(packages) == 0:
            break
        for package in packages:
            num_items_processed += 1
            session = create_session()
            summary_response = api.get_bill_summary(package['packageId'])['data']
            bill_slug = str(summary_response['billType']) + str(summary_response['billNumber'])
            bill_id = '{0}-{1}'.format(bill_slug, str(summary_response['congress']))
            item, created = get_or_create(session, Bill, bill_slug=bill_slug, bill_id=bill_id,
                                          congress=int(summary_response['congress']),
                                          defaults={'title': summary_response['title']})
            if created:
                num_bills_created += 1
                print('Processed bill creation for item #{0}. {1} bills created'.format(str(num_items_processed),
                                                                                        str(num_bills_created)))
            else:
                print('Found bill for item #{0}'.format(str(num_items_processed)))
            session.commit()
            version, created = get_or_create(session, BillVersion, bill=item.bill_id,
                                             title=str(summary_response['billVersion']).upper())
            if created:
                num_versions_created += 1
                print(
                    'Processed version creation for item #{0}. {1} versions created'.format(str(num_items_processed),
                                                                                            str(num_versions_created))
                )
            else:
                print('Found version for item #{0}'.format(str(num_items_processed)))
            session.commit()
            if version.full_text is None:
                num_full_text_pulled += 1
                full_text_response = api.get_bill_full_text(package['packageId'])
                parser = MyHTMLParser()
                result = parser.run_feeder(full_text_response['data'].decode())
                result = parser.run_feeder(full_text_response['data'].decode())
                version.full_text = result
                print(
                    'Processed full text addition for item #{0}. {1} full texts added'.format(str(num_items_processed),
                                                                                              str(num_full_text_pulled))
                )
                session.commit()
            session.close()
        offset += 100


def run_thing():
    for i in range(110, 118):
        versions = ['as', 'ash', 'ath', 'ats', 'cdh', 'cds', 'cph', 'cps', 'eah', 'eas', 'eh', 'eph', 'enr', 'es',
                    'fah', 'fph', 'fps', 'hdh', 'hds', 'ih', 'iph', 'ips', 'is', 'lth', 'lts', 'oph', 'ops', 'pav',
                    'pch', 'pcs', 'pp', 'pap', 'pwah', 'rah', 'ras', 'rch' 'rcs', 'rdh', 'reah', 'res', 'renr', 'rfh',
                    'rfs', 'rh','rih', 'ris', 'rs', 'rth', 'rts', 'sas', 'sc']
        doc_classes = ['hconres', 'hjres', 'hr', 'hres', 's', 'sconres', 'sjres', 'sres']
        for version in versions:
            for doc_class in doc_classes:
                do_things(i, version, doc_class)
