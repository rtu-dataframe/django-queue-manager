import base64
import pickle
import inspect
import socket

from django_queue_manager import models


# Defines the Task Class
from django_queue_manager.models import DQMQueue


class Task(object):
	def __init__(self, a_callable, *args, dqmqueue=None, **kwargs):
		assert callable(a_callable)

		if not dqmqueue:
			#Use the default DQMQueue
			dqmqueue = DQMQueue.objects.first()

		self.task_function_name = "{module}.{function}".format(module=inspect.getmodule(a_callable).__name__,
		                                                       function=a_callable.__name__)
		self.task_callable = a_callable
		self.args = args
		self.kwargs = kwargs
		self.dqmqueue = dqmqueue
		self.db_id = None

	def run(self):
		self.task_callable(*self.args, **self.kwargs)


# Defines the TaskManager class with the methods in order to manage them(Task)
class TaskManager:
	@staticmethod
	def unpack(pickled_task):
		'''Used to get back the picked tasks'''
		new_task = pickle.loads(base64.b64decode(pickled_task))
		assert isinstance(new_task, Task)
		return new_task

	@staticmethod
	def serialize_task(task):
		'''Used to serialize tasks'''
		return base64.b64encode(pickle.dumps(task))

	@staticmethod
	def save_task_to_db(new_task):
		'''Used to save enqueued tasks'''
		task_to_enqueue = models.QueuedTasks(task_function_name=new_task.task_function_name,
		                                     task_args="{args}".format(args=new_task.args),
		                                     task_kwargs="{kwargs}".format(kwargs=new_task.kwargs),
		                                     pickled_task=TaskManager.serialize_task(new_task),
		                                     dqmqueue=new_task.dqmqueue)
		task_to_enqueue.save()
		new_task.db_id = task_to_enqueue.pk
		return new_task

	@staticmethod
	def save_task_failed(task, exception):
		'''Used to save failed state tasks'''
		task_failed = models.FailedTasks(task_function_name=task.task_function_name, task_args=task.args,
		                                 task_kwargs=task.kwargs,
		                                 task_id=task.db_id, exception=exception,
		                                 pickled_task=TaskManager.serialize_task(task),
		                                 dqmqueue=task.dqmqueue)
		task_failed.save()

	@staticmethod
	def save_task_success(task):
		'''Used to save successful state tasks'''
		task_success = models.SuccessTasks(task_function_name=task.task_function_name, task_args=task.args,
		                                   task_kwargs=task.kwargs, task_id=task.db_id,
		                                   pickled_task=TaskManager.serialize_task(task),
		                                   dqmqueue=task.dqmqueue)
		task_success.save()

	@staticmethod
	def delete_enqueued_task(task):
		'''Used to delete tasks'''
		task_to_delete = models.QueuedTasks.objects.get(pk=task.db_id)
		task_to_delete.delete()

	@staticmethod
	def delete_failed_task(task):
		'''Used to delete tasks'''
		task_to_delete = models.FailedTasks.objects.get(pk=task.db_id)
		task_to_delete.delete()

	@staticmethod
	def retry_failed_task(task):
		'''Used to retry failed task'''

		#Unpacking the task
		unpacked_task = TaskManager.unpack(task.pickled_task)
		#Save a new istance of task to the Default Queue
		requeued_task = TaskManager.save_task_to_db(unpacked_task)

		#Deletes the task
		task_to_delete = models.FailedTasks.objects.get(pk=task.pk)
		task_to_delete.delete()

		TaskManager.send_to_queue(requeued_task)

	@staticmethod
	def requeue_task(task):
		'''Used to retry failed task'''

		#Unpacking the task
		unpacked_task = TaskManager.unpack(task.pickled_task)
		#Save a new istance of task to the Default Queue
		requeued_task = TaskManager.save_task_to_db(unpacked_task)

		#Deletes the task
		task_to_delete = models.QueuedTasks.objects.get(pk=task.pk)
		task_to_delete.delete()

		TaskManager.send_to_queue(requeued_task)

	@staticmethod
	def send_to_queue(task):
		# Creates the socket connection to the specified Server and Port
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((task.dqmqueue.queue_host, task.dqmqueue.queue_port))
		sock.send(TaskManager.serialize_task(task))

		# Checks that the socket acquired correctly the Task
		received = sock.recv(1024)
		sock.close()

		return received
