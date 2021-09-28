from util.cred_handler import get_secret
import binascii
from binascii import hexlify, unhexlify
from hashlib import pbkdf2_hmac
from os import urandom
from db.models import User
from db.db_utils import get_single_object

class BadAuthTokenException(Exception):
    """ Raised when an invalid authentication token is passed """
    pass


def secure_string():
    return hexlify(urandom(16)).decode("ascii")


def secure_hash(token: str):
    try:
        return hexlify(
            pbkdf2_hmac(
                "sha256", unhexlify(token), unhexlify(get_secret("hash_salt")), 100000
            )
        )[0:32]
    except binascii.Error:
        return None

def get_serialized_user_by_token(token: str, session):

    hash = secure_hash(token=token)
    user_object = get_single_object(session, User, key_hash=hash)
    if not user_object is None:
        serialized = user_object.to_dict()
        session.close()
        return serialized
    else:
        session.close()
        raise BadAuthTokenException


def is_valid_user(token: str, session):
    hash = secure_hash(token)
    user_object = get_single_object(session, User, key_hash=hash)
    if not user_object is None:
        return True
    else:
        raise BadAuthTokenException


def get_token(request):
    """
    Get the token from the headers of a request
    :param request: request hitting endpoint
    :return: token as a string
    """
    headers = request.headers
    bearer = headers.get('Authorization')
    if bearer is None:
        return None
    return bearer.split()[1]
