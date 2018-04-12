import logging
import socket
from django_queue_manager.task_manager import Task, TaskManager

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s', )


def push_task_to_queue(a_callable, *args, dqmqueue=None, **kwargs):
    # Create a new task istance
    new_task = Task(a_callable, *args, dqmqueue=dqmqueue, **kwargs)
    new_task = TaskManager.save_task_to_db(new_task)  # returns with db_id

    received = send_task_to_queue(new_task)

    return received


def send_task_to_queue(task):
    try:
        logging.info('Sending task {id} to socket {socket_address}:{socket_port}'.format(
            id=task.db_id,
            socket_address=task.dqmqueue.queue_host,
            socket_port=task.dqmqueue.queue_port))

        task_result = TaskManager.send_to_queue(task)

        logging.info('Task {id} sent.'.format(id=task.db_id))

        return task_result
    except Exception as ex:
        logging.warning(
            'Socket {socket_address}:{socket_port} Exception: {ex}, anyway, the task is on the db, '
            'ready to be requeued manually'.format(
                socket_address=task.dqmqueue.queue_host,
                socket_port=task.dqmqueue.queue_port,
                ex=ex))
        return None
