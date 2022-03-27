import requests
import time
import backoff

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

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries=10)
    def search_tweets_archive(self, query: str, start_time: str, end_time: str, next_token: str = None):
        """ Searches for tweets from twitter archive

        Args:
            query (str): A query string, formatted using the twitter API standard
            start_time (str): Start date in format YYYY-MM-DD
            end_time (str): End date in format YYYY-MM-DD
            next_token (str, optional): Next token for Twitter's API. Defaults to None.

        Returns:
            (Response Code, Twitter API response)
        """
        query = query.replace('and', '').replace('or', '')
        args = {
            # Always add no retweets, no reason to pull those, and they affect our limits
            'query': "{0} -is:retweet".format(query),
            # Various tweet fields to pull, don't edit unless necessary
            'tweet.fields': 'author_id,created_at,lang,referenced_tweets,source,in_reply_to_user_id,public_metrics,context_annotations,entities',
            'max_results': 100,
            'start_time': '{0}T00:00:00Z'.format(start_time),
            'end_time': '{0}T23:59:59Z'.format(end_time)
        }
        if next_token is not None:
            args['next_token'] = next_token
        response = self.request_get('tweets/search/all', args=args)
        return response

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries=10)
    def get_user_by_id(self, user_id: int):
        """ Get an individual twitter user by ID

        Args:
            user_id (int): Twitter User ID

        Returns:
            (Response Code, Twitter API response)
        """
        args = {
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,'
                           'protected,public_metrics,url,username,verified,withheld'
        }
        return self.request_get('users/{0}'.format(str(user_id)), args=args)

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries=10)
    def get_users_by_ids(self, user_ids: str):
        """ Get multiple twitter users info at once

        Args:
            user_ids (str): Comma separated string of twitter IDs, max of 100

        Returns:
            (Response Code, Twitter API Response)
        """
        args = {
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,'
                           'protected,public_metrics,url,username,verified,withheld'
        }
        return self.request_get('users?ids={0}'.format(user_ids), args=args)

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries=10)
    def get_user_by_username(self, username: str):
        """ Get single twitter user information from username

        Args:
            username (str): Twitter username

        Returns:
            (Response Code, Twitter API Response)
        """
        args = {
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,'
                           'protected,public_metrics,url,username,verified,withheld'
        }
        return self.request_get('users/by/username/{0}'.format(str(username)), args=args)