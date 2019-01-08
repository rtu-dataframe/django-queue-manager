#  Based on the Worker class from Python in a nutshell, by Alex Martelli
import logging
import threading
import queue as Queue
import uuid

import time
from django_queue_manager.task_manager import TaskManager
from django.conf import settings
SAVE_SUCCESS_TASKS = getattr(settings, "SAVE_SUCCESS_TASKS", True)

from django_queue_manager.utilities.loggers import get_default_logger
logger = get_default_logger(__name__)


class Worker(threading.Thread):
    def __init__(self):

        threading.Thread.__init__(self, name=str(uuid.uuid4()))
        self._stopevent = threading.Event()
        self.setDaemon(True)
        self.worker_queue = Queue.Queue()
        self.tasks_counter = 0

        self.logger = logging

        self.start()

    def put_task_on_queue(self, new_pickled_task):

        try:
            new_task = TaskManager.unpack(new_pickled_task)
            self.tasks_counter += 1
            self.worker_queue.put(new_task)
            return True, "sent"
        except Exception as e:
            return False, "Worker: {0}".format(e)

    def run_task(self, task):

        for i in range(task.dqmqueue.max_retries):
            try:
                task.run()
                break
            except:
                if i < task.dqmqueue.max_retries - 1:
                    pass
                else:
                    raise

    def stop_thread(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        if self.worker_queue != None:
            self._stopevent.set()
            self.logger.warning('Worker stop event set')
            return "Stop Set"
        else:
            return "Worker Off"

    def ping(self):
        if self.worker_queue != None:
            return "I'm OK"
        else:
            return "Worker Off"

    def status_waiting(self):
        return self.worker_queue.qsize()

    def status_handled(self):
        # all, success & failes
        return self.tasks_counter

    def run(self):
        # The code above will run indefinitely except when a thread _stopevent.isSet(), it will try to empty
        # the queue and move the task into success/failed tasks in base of successful or not execution.
        self.logger.info('Worker Thread Starts')
        while not self._stopevent.isSet():
            if not self.worker_queue.empty():
                try:
                    task = self.worker_queue.get()
                    self.logger.info('Consuming Task Id: {db_id}'.format(
                        name=task.task_function_name,
                        db_id=task.db_id))
                    self.run_task(task)

                    # Save it on the success table
                    if SAVE_SUCCESS_TASKS:
                        TaskManager.save_task_success(task)
                        self.logger.info(
                            'Task Id {db_id} success!'.format(name=task.task_function_name,
                                                              db_id=task.db_id))
                except Exception as e:
                    # Save it on the failed table
                    TaskManager.save_task_failed(task, e)

                    self.logger.warning(
                        'Task Id {db_id} failed!'.format(name=task.task_function_name,
                                                         db_id=task.db_id))
                    # Continue the loop if the task throw an exception
                    continue

                finally:
                    # In any case, it will dequeue the task form the queued tasks
                    self.dequeue_task(task=task)

                    # Close the connection, in order to prevent (2006, 'MySQL server has gone away') timeout error
                    from django.db import connection
                    connection.close()

            else:
                # In order to respect the CPU sleeps for 50 milliseconds when the queue it's empty
                time.sleep(0.100)

        self.worker_queue = None
        self.logger.warning('Worker Thread stopped, {0} tasks handled'.format(self.tasks_counter))

    def dequeue_task(self, task):
        # Removes the enqueued task from the DB after execution or failure
        TaskManager.delete_enqueued_task(task)
        self.logger.info('Removing Task Id {db_id} from enqueued tasks!'.format(
            name=task.task_function_name,
            db_id=task.db_id))
