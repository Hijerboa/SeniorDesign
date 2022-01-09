from db.database_connection import initialize, create_session
import pymysql
pymysql.install_as_MySQLdb()
from db.models import Bill

def fuck_you_nick():
    initialize()
    session = create_session()
    bills = session.query(Bill).limit(50).all()
    for bill in bills:
        print(bill.bill_slug)