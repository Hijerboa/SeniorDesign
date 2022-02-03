from tasks.propublica_tasks import get_bill_data_by_congress


def run():
    get_bill_data_by_congress(117, 'both')
