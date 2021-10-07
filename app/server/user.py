from db.database_connection import create_session
from authorization.auth_utils import get_token, BadAuthTokenException, is_valid_user, secure_hash, \
    does_user_have_permission
from util.make_error import make_error
from db.db_utils import get_single_object
from db.models import User

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)

bp = Blueprint('user', __name__)

@bp.route('/me', methods=(['GET']))
def get_me():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'self_profile'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    user_dict = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role
    }
    session.close()
    return jsonify(user_dict)