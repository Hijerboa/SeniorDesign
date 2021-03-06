from db.database_connection import initialize, create_session, Base
from util.cred_handler import get_secret
from authorization.auth_utils import secure_string, secure_hash, get_serialized_user_by_token
from initializer.initializer_utils import is_initial_admin_present
import db.models as models
from time import sleep

initialize()

# Creates an initial user
def create_initial_user(session):
    token = secure_string()
    session.add(models.User(name='admin', email=get_secret('initial_admin_email'), key_hash=secure_hash(token), role='admin'))
    session.commit()
    return token


# Run from initializer, any startup tasks can be run here
def perform_initial_tasks():
    session = create_session()
    if not is_initial_admin_present():
        print(create_initial_user(session=session))
    session.close()
