from db.database_connection import create_session
from authorization.auth_utils import get_token, does_user_have_permission, secure_hash
from util.make_error import make_error
from tasks.machine_learning_tasks import keyword_extraction_by_bill
from db.db_utils import get_single_object
from db.models import User, Bill
from flask import Blueprint, request, jsonify

bp = Blueprint('ml', __name__)


@bp.route('/bill_keywords', methods=(['GET']))
def stream_search():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    bill_param = request.args.get('bill_id')
    if bill_param is None:
        return make_error(405, 1, "No Bill", "Add a bill parameter")
    session.commit()
    object = get_single_object(session, Bill, bill_id=bill_param)
    if object is None:
        return make_error(400, 1, 'Invalid Bill', 'Invalid bill')
    keyword_extraction_by_bill.apply_async((bill_param,))
    session.close()
    return jsonify('Task has been created and queued')
