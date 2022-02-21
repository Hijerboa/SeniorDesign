from db.models import User
from db.database_connection import create_session
from db.db_utils import get_multiple_objects


# Checks whether at least one admin user is present
def is_initial_admin_present():
    session = create_session()
    users = get_multiple_objects(session, User)
    found = False
    for user in users:
        if user.role == 'admin':
            found = True
            break
    session.close()
    return found