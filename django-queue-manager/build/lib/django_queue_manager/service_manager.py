import time
from django_queue_manager import worker_manager
from django_queue_manager.models import DQMQueue
from django_queue_manager.server_manager import TaskSocketServerThread

class ServiceManager:

	def service_start(self):

		worker_manager.start()
		server_thread = TaskSocketServerThread('localhost', DQMQueue.objects.first().queue_port)
		time.sleep(5)
		socket_server = server_thread.socket_server()
		socket_server.serve_forever()



if __name__ == "__main__":
	#Starts the worker manager and the server thread manager on the specified port
	ServiceManager().service_start()