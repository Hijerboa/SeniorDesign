from db.models import Bill
from db.database_connection import initialize, create_session


# A script to make requests to the API server to launch the keyword extraction
def launch_keyword_extraction():
    initialize()
    session = create_session()
    bills = session.query(Bill).limit(100).all()
