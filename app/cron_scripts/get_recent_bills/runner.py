from tasks.propublica_tasks import run_get_bill_data_by_congress


def run():
    run_get_bill_data_by_congress.apply_async((117, 'both',))
