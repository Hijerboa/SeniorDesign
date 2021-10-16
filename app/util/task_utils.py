from db.db_utils import get_single_object, create_single_object
from db.models import Task

def create_task_db_object(task_creator: int, task_type: str, task_message: str, task_id: str, session):
    return create_single_object(session, Task, task_id=task_id, defaults={
        'user_id': task_creator,
        'task_type': task_type,
        'status': 'PENDING',
        'message': task_message
    })
