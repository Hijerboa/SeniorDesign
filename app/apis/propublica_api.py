import requests

"""
Basic API client for the Propublica API with a response handler and convenience methods
"""


class PropublicaAPIError(Exception):
    """API returned an unsuccessful status code"""
    pass


def handle_propublica_response(response: requests.Response, raw_out: bool, ignore_errors=False):
    """
    Handles responses from the Propublica API
    :param response: response from requests
    :param raw_out: Bypass function if true
    :param ignore_errors: Ignore errors if true
    :return: Processed Response
    """
    try:
        data = response.json()
    except Exception:
        data = None

    if raw_out:
        return response
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

    def get_congress_members(self, congress_number: int, chamber: str):
        return self.request_get('{0}/{1}/members.json'.format(str(congress_number), chamber))