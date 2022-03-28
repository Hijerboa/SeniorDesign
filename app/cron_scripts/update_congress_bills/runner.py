from db.database_connection import initialize, create_session
from db.models import Bill
from tasks.propublica_tasks import run_get_and_update_bill


def run():
    initialize()
    session = create_session()

    bills = session.query(Bill).filter(Bill.active == True, Bill.congress == 117)
    for bill in bills:
        run_get_and_update_bill.apply_async((bill.bill_id, 1,))
    session.close()
