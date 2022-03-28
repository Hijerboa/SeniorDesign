from tasks.task_initializer import CELERY
from db.database_connection import create_session
from db.db_utils import get_or_create, create_single_object, get_single_object
from db.models import Bill, BillVersion, Task, TaskError
from apis.govinfo_api import GovInfoAPI
from util.cred_handler import get_secret
from html.parser import HTMLParser

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
    
    
@CELERY.task()
def run_get_versions(congress: int, bill_version: str, doc_class: str, offset: int, user_id: int):
    session = create_session()
    task = get_versions(congress, bill_version, doc_class, offset, user_id)
    session.add(task)
    session.commit()
    res = task.run()
    session.commit()
    session.close()
    return res


@CELERY.task()
def rerun_get_versions(task_id: int, user_id):
    session = create_session()
    task: Task = get_single_object(session, Task, id=task_id)
    task = get_versions(task.parameters['congress'], task.parameters['bill_version'], task.parameters['doc_class'], task.parameters['offset'])
    session.add(task)
    session.commit()
    res = task.run()
    session.commit()
    session.close()
    return res

class get_versions(Task):
    def __init__(self, congress: int, bill_version: str, doc_class, offset: int, user_id: int):
        self.user_id = user_id
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='congress_api_get_versions', parameters={'congress': congress, 'bill_version': bill_version, 'doc_class': doc_class, 'offset': offset})
        
    def run(self):
        session = create_session()
        try:
            result = self.get_versions(self.parameters['congress'], self.parameters['bill_version'], self.parameters['doc_class'], self.parameters['offset'])
            session.close()
            return result
        except Exception as e:
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            session.commit()
            session.close()
            return str(e)
        
        
    def get_versions(self, congress: int, bill_version: str, doc_class, offset: int):
        api: GovInfoAPI = GovInfoAPI(get_secret('gov_info_url'), get_secret('gov_info_key'))
        session = create_session()
        start_string = '1999-01-01T00:00:00Z'
        end_date = '2023-01-01T00:00:00Z'
        response = api.get_bill_listing(start_string, end_date, offset, congress, bill_version, doc_class)
        packages = response['data']['packages']
        for package in packages:
            summary_response = api.get_bill_summary(package['packageId'])['data']
            bill_slug = str(summary_response['billType']) + str(summary_response['billNumber'])
            bill_id = '{0}-{1}'.format(bill_slug, str(summary_response['congress']))
            item, created = get_or_create(session, Bill, bill_slug=bill_slug, bill_id=bill_id,
                                            congress=int(summary_response['congress']),
                                            defaults={'title': summary_response['title']})
            session.commit()
            version, created = get_or_create(session, BillVersion, bill=item.bill_id,
                                                title=str(summary_response['billVersion']).upper())
            session.commit()
            if version.full_text is None:
                full_text_response = api.get_bill_full_text(package['packageId'])
                parser = MyHTMLParser()
                result = parser.run_feeder(full_text_response['data'].decode())
                result = parser.run_feeder(full_text_response['data'].decode())
                version.full_text = result
                session.commit()
        session.close()
        if len(packages) == 100:
            run_get_versions.apply_async((congress, bill_version, doc_class, offset+100, 1))
        return f'{len(packages)} collected'
