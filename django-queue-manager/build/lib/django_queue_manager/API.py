import socket
from django_queue_manager.task_manager import Task, TaskManager


def push_task_to_queue(a_callable, dqmqueue=None, *args, **kwargs):
    # Create a new task istance
    new_task = Task(a_callable, dqmqueue=dqmqueue, *args, **kwargs)
    new_task = TaskManager.save_task_to_db(new_task)  # returns with db_id

    received = TaskManager.send_to_queue(new_task)

    return received
