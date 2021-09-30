import requests

"""
Basic API client for the Twitter API with a response handler and convenience methods
"""


class TwitterAPIError(Exception):
    """API returned an unsuccessful status code"""
    pass


def handle_twitter_response(response: requests.Response, raw_out: bool, ignore_errors=False):
    """
    Handles responses from the Twitter API
    :param response: reponse from requests
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
        raise TwitterAPIError(response.status_code, data)
    return {'status': response.status_code, 'data': data}


class TwitterAPI:
    def __init__(self, twitter_url: str, bearer_token: str):
        self.twitter_url = twitter_url
        self.api_headers = {'Authorization': 'Bearer {0}'.format(bearer_token)}

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

        url = self.twitter_url + sub_path

        response = requests.get(url, params=args, headers=self.api_headers)
        return handle_twitter_response(response, raw_out, ignore_errors)

    def search_tweets(self, query: str, next_token: str = None):
        args = {
            'query': "{0} -is:retweet".format(query),
            'tweet.fields': 'author_id,created_at,lang,referenced_tweets,source,in_reply_to_user_id,public_metrics',
            'max_results': 100
        }
        if next_token is not None:
            args['next_token'] = next_token
        return self.request_get('tweets/search/recent', args=args)
