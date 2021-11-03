from datetime import datetime


def check_time(time: str) -> bool:
    try:
        datetime.strptime(time, '%Y-%m-%d')
        return True
    except ValueError:
        return False
