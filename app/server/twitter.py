from db.database_connection import create_session
from authorization.auth_utils import get_token, does_user_have_permission, secure_hash
from util.make_error import make_error
from tasks.twitter_tasks import retrieve_user_info_by_id, retrieve_user_info_by_username, \
    retrieve_users_info_by_ids, tweet_puller_archive
from db.models import User
from db.db_utils import get_single_object, create_single_object
from util.check_time import check_time
from flask import Blueprint, request, jsonify

bp = Blueprint('twitter', __name__)


@bp.route('/tweets/archive/search', methods=(['GET']))
def archive_search():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    query_param = request.args.get('query')
    if query_param is None:
        return make_error(405, 1, "No Query", "Add a query parameter")
    start_param = request.args.get('start')
    if start_param is None:
        return make_error(405, 2, "No start date", "Add a start parameter")
    if not check_time(start_param):
        return make_error(405, 3, "Malformed start date", "Send parameter in YYYY-MM-DD format")
    end_param = request.args.get('end')
    if end_param is None:
        return make_error(405, 2, "No end date", "Add an end parameter")
    if not check_time(start_param):
        return make_error(405, 3, "Malformed end date", "Send parameter in YYYY-MM-DD format")
    session.commit()
    tweet_puller_archive.apply_async((query_param, None, start_param, end_param,), countdown=3.5)
    session.close()
    return jsonify('Task has been created and queued')



@bp.route('/users/lookup/by_id/single', methods=(['GET']))
def single_user_lookup():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    user_param = request.args.get('user')
    if user_param is None:
        return make_error(405, 1, "No user", "Add a user parameter")
    retrieve_user_info_by_id.apply_async((user_param,), countdown=3)
    session.commit()
    session.close()
    return jsonify("Task created")


@bp.route('/users/lookup/by_username/single', methods=(['GET']))
def single_user_lookup_username():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    user_param = request.args.get('username')
    if user_param is None:
        return make_error(405, 1, "No user", "Add a user parameter")
    retrieve_user_info_by_username.apply_async((user_param,), countdown=3.5)
    session.commit()
    session.close()
    return jsonify("Task created")


@bp.route('/users/lookup/by_id/multiple', methods=(['GET']))
def multiple_user_lookup():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    users_param = request.args.get('users')
    if users_param is None:
        return make_error(405, 1, "No user", "Add a user parameter")
    retrieve_users_info_by_ids.apply_async((users_param,), countdown=3)
    session.commit()
    session.close()
    return jsonify("Task created")
