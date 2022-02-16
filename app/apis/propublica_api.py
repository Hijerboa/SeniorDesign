import requests
import backoff
import json
from json.decoder import JSONDecodeError

"""
Basic API client for the Propublica API with a response handler and convenience methods
"""


class PropublicaAPIError(Exception):
    """API returned an unsuccessful status code"""
    pass

class PropublicaAPITimeoutError(Exception):
    """API took too long to respond"""
    pass

def handle_propublica_response(response: requests.Response, raw_out: bool, ignore_errors=False):
    """
    Handles responses from the Propublica API
    :param response: response from requests
    :param raw_out: Bypass function if true
    :param ignore_errors: Ignore errors if true
    :return: Processed Response
    """
    in_data = response.content.decode()
    try:
        data = json.loads(in_data)
    except JSONDecodeError:
        string = in_data
        result = string.replace("\\ ", "\\\\")
        data = json.loads(result, strict=False)
    except Exception:
        data = None

    if raw_out:
        return response
    if response.status_code == 504 and not ignore_errors:
        raise PropublicaAPITimeoutError
    if not response.ok and not ignore_errors:
        raise PropublicaAPIError(response.status_code, data)
    return {'status': response.status_code, 'data': data}


class ProPublicaAPI:
    def __init__(self, propublica_url: str, bearer_token: str):
        self.propublica_url = propublica_url
        self.api_headers = {'X-API-Key': '{0}'.format(bearer_token)}

    def request_get(
            self,
            sub_path: str,
            args=None,
            raw_out=False,
            ignore_errors=False,
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

        url = self.propublica_url + sub_path

        response = requests.get(url, params=args, headers=self.api_headers)
        return handle_propublica_response(response, raw_out, ignore_errors)

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException, PropublicaAPITimeoutError),
                          max_tries=10)
    def get_congress_members(self, congress_number: int, chamber: str):
        """ Get the congress members for a specified congress in a specified chamber

        Args:
            congress_number (int): number, between 109 and 117
            chamber (str): 'senate' or 'house'

        Returns:
            (Response Code, Propublica API Response)
        """
        return self.request_get('{0}/{1}/members.json'.format(str(congress_number), chamber))

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException, PropublicaAPIError),
                          max_tries=10)
    def get_recent_bills(self, congress_number: int, chamber: str, offset: int):
        """Get bills from a specified congress and chamber. 10 are returned at a time

        Args:
            congress_number (int): 109-117
            chamber (str): 'senate', 'house', or 'both'
            offset (int): Offset

        Returns:
            (Response Code, Propublica API Response)
        """
        args = {
            'offset': str(offset)
        }
        return self.request_get('{0}/{1}/bills/introduced.json'.format(str(congress_number), chamber), args=args)

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException, PropublicaAPITimeoutError),
                          max_tries=10)
    def get_bill_activity(self, bill_slug: str, congress: int):
        """Get the bill activity and versions for a specified bill

        Args:
            bill_slug (str): Bill slug
            congress (int): Congress number, 109-117

        Returns:
            (Response Code, Propublica API Response)
        """
        return self.request_get('{0}/bills/{1}.json'.format(str(congress), bill_slug))
