import requests
import backoff

"""
Basic API client for the GovInfo API with a response handler and convenience methods
"""


class GovInfoAPIError(Exception):
    """API returned an unsuccessful status code"""
    pass

class GovInfoAPITimeoutError(Exception):
    """API took too long to respond"""
    pass

def handle_gov_info_response(response: requests.Response, raw_out: bool, ignore_errors=False, json=True):
    """
    Handles responses from the GovInfo API
    :param response: response from requests
    :param raw_out: Bypass function if true
    :param ignore_errors: Ignore errors if true
    :return: Processed Response
    """
    if json:
        try:
            data = response.json()
        except Exception:
            data = None
    else:
        try:
            data = response.content
        except Exception:
            data = None

    if raw_out:
        return response
    if response.status_code == 504 and not ignore_errors:
        raise GovInfoAPITimeoutError
    if not response.ok and not ignore_errors:
        raise GovInfoAPIError(response.status_code, data)
    return {'status': response.status_code, 'data': data}


class GovInfoAPI:
    def __init__(self, gov_info_url: str, bearer_token: str):
        self.gov_info_url = gov_info_url
        self.api_headers = {'Authorization': 'Bearer {0}'.format(bearer_token)}

    def request_get(
            self,
            sub_path: str,
            args=None,
            raw_out=False,
            ignore_errors=False,
            json=True
    ):
        """
        Perform a get request
        :param sub_path: subpath for URL
        :param args: query string params
        :param raw_out: Return raw response instead of decoded json
        :param ignore_errors: ignore errors
        :return: The response, potentially decoded
        """

        if args is None:
            args = {}

        url = self.gov_info_url + sub_path

        response = requests.get(url, params=args, headers=self.api_headers)
        if not json:
            return handle_gov_info_response(response, raw_out, ignore_errors, json=False)
        return handle_gov_info_response(response, raw_out, ignore_errors)
    
    # All functions us backoff decorators to ensure retry on random errors that the API sometimes returns

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException, GovInfoAPITimeoutError),
                          max_tries=10)
    def get_bill_full_text(self, bill_slug: str):
        """Returns bill full text in an HTML format

        Args:
            bill_slug (str): Formatted bill slug, obtained from govinfo API.

        Returns:
            (Response Code, GovInfo API Response)
        """
        return self.request_get('/packages/{0}/htm'.format(bill_slug), json=False)
    

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException, GovInfoAPITimeoutError),
                          max_tries=10)
    def get_bill_listing(self, start_date: str, end_date: str, offset: int, congress: int, version: str, doc_class: str):
        """Returns listing of bill versions

        Args:
            start_date (str): Start date
            end_date (str): End Date
            offset (int): Offset (cannot be greator than 50,000 since the GovInfo API is stupid)
            congress (int): Congress number (usually 117)
            version (str): Bill version, can be one of the following: ['as', 'ash', 'ath', 'ats', 'cdh', 'cds', 'cph', 'cps', 'eah', 'eas', 'eh', 'eph', 'enr', 'es',
                    'fah', 'fph', 'fps', 'hdh', 'hds', 'ih', 'iph', 'ips', 'is', 'lth', 'lts', 'oph', 'ops', 'pav',
                    'pch', 'pcs', 'pp', 'pap', 'pwah', 'rah', 'ras', 'rch' 'rcs', 'rdh', 'reah', 'res', 'renr', 'rfh',
                    'rfs', 'rh','rih', 'ris', 'rs', 'rth', 'rts', 'sas', 'sc']
            doc_class (str): Document class. Can be one of the following: ['hconres', 'hjres', 'hr', 'hres', 's', 'sconres', 'sjres', 'sres']
        
        This is arguably not efficient, as many requests are made for small numbers of bills returned. But becuase the offset can't be more than 50K, this 
        seems like the best way to handle it

        Returns:
            (Response Code, GovInfo API Response)
        """
        args = {
            'offset': offset,
            'pageSize': 100,
            'congress': congress,
            'billVersion': version,
            'docClass': doc_class
        }
        return self.request_get('/collections/BILLS/{0}/{1}'.format(str(start_date), str(end_date)), args=args)

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException, GovInfoAPITimeoutError),
                          max_tries=10)
    def get_bill_summary(self, bill_slug: str):
        """Returns bill summary of requested bill

        Args:
            bill_slug (str): bill slug from GovInfoAPI

        Returns:
            (Response Code, GovInfo API Response)
        """
        return self.request_get('/packages/{0}/summary'.format(bill_slug))

