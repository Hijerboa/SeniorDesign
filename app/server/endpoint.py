import functools
from db.database_connection import create_session
from authorization.auth_utils import get_token, BadAuthTokenException, is_valid_user
from util.make_error import make_error
from server.tasks import tweet_puller, retrieve_user_info_by_id, retrieve_users_info_by_ids

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)

bp = Blueprint('endpoint', __name__, url_prefix='/')


@bp.route('/', methods=(['GET']))
def main_page():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, "No access token provided", "Provide access token")
    try:
        user = is_valid_user(token, session)
        query_param = request.args.get('query')
        if query_param is None:
            return make_error(405, 1, "No Query", "Add a query parameter")
        tweet_puller.delay(query_param)
        session.close()
        return jsonify("Task created")
    except BadAuthTokenException:
        session.close()
        return make_error(403, 1, "Unauthorized access token", "Contact Nick")


@bp.route('/user_lookup', methods=(['GET']))
def user_lookup():
    session=create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, "No access token provided", "Provide access token")
    try:
        user = is_valid_user(token, session)
        user_param = request.args.get('user')
        if user_param is None:
            return make_error(405, 1, "No user", "Add a user parameter")
        retrieve_user_info_by_id.delay(user_param)
        session.close()
        return jsonify("Task created")
    except BadAuthTokenException:
        session.close()
        return make_error(403, 1, "Unauthorized access token", "Contact Nick")


@bp.route('/multiple_user_lookup', methods=(['GET']))
def multiple_user_lookup():
    session=create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, "No access token provided", "Provide access token")
    try:
        user = is_valid_user(token, session)
        users_param = request.args.get('users')
        if users_param is None:
            return make_error(405, 1, "No user", "Add a user parameter")
        retrieve_users_info_by_ids.delay(users_param)
        session.close()
        return jsonify("Task created")
    except BadAuthTokenException:
        session.close()
        return make_error(403, 1, "Unauthorized access token", "Contact Nick")
