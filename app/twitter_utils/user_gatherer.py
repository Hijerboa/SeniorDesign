import datetime
from db.db_utils import get_or_create
from db.models import TwitterUser
from sqlalchemy.exc import IntegrityError

import logging

logger = logging.getLogger(__name__)

class InvalidTwitterUser(Exception):
    """Raised if a twitter user does not exist"""
    pass


def create_user_object(user_info: dict, session):
    user_stats = user_info.pop('public_metrics')
    if 'entities' in user_info.keys():
        user_info.pop('entities')
    if 'pinned_tweet_id' in user_info.keys():
        user_info.pop('pinned_tweet_id')
    if 'includes' in user_info.keys():
        user_info.pop('includes')
    if 'errors' in user_info.keys():
        user_info.pop('errors')
        raise InvalidTwitterUser
    if 'withheld' in user_info.keys():
        user_info.pop('withheld')
    user_info['created_at'] = datetime.datetime.strptime(user_info['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    user_info['followers_count'] = user_stats['followers_count']
    user_info['following_count'] = user_stats['following_count']
    user_info['tweet_count'] = user_stats['tweet_count']
    user_info['listed_count'] = user_stats['listed_count']
    user_info['display_name'] = user_info['name']
    user_info.pop('name')
    try:
        user_object, created = get_or_create(session, TwitterUser, id=user_info['id'], defaults=user_info)
        session.commit()
        logger.error(user_object.id)
    except IntegrityError:
        pass
    return user_object
