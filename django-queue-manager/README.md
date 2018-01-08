
# Django Queue Manager


**A simple async tasks queue via a django app and SocketServer, zero
configs.**

 - [Why?](#why)
   
 - [Overview](#Overview)
        
 - [Install](#Install)
       
 - [Settings](#Settings)
          
 - [Run the Tasks Queue Server](#Run-the-Tasks-Queue-Server)
            
 - [Persistency](#Persistency)
   
 - [Run the Tasks Queue on Another Server](#Run-the-Tasks-Queue-on-Another-Server)

## <a name="why"></a>Why?

Although Celery is pretty much the standard for a django tasks queue
solution, it can be complex to install and config.

The common case for a web application queue is to send emails: you don't
want the django thread to wait until the SMTP, or email provider API,
finishes. But to send emails from a site without a lot of traffic, or to
run other similar simple tasks, you don't need Celery.

This queue app is a simple, up and running queueing solution. The more
complex distributed queues can wait until the website has a lot of
traffic, and the scalability is really required.

In addition, the Django-queue-manager provides a simple and stunning easy-to-use interface in the admin backend page


## <a name="Overview"></a>Overview:


In a nutshell, a python SocketServer runs in the background, and listens
to a tcp socket. SocketServer gets the request to run a task from it's
socket, puts the task on a Queue. A Worker thread picks tasks from this
Queue, and runs the tasks one by one.

The SocketServer istance can be one or multiple, depending on your app requirements.

You send a task request to the default SocketServer with:


    from mysite.django-queue-manager.API import push_task_to_queue
    ...
    push_task_to_queue(a_callable, *args, **kwargs)

Sending email might look like:

    push_task_to_queue(send_mail,subject="foo",message="baz",recipient_list=[user.email])

If you have more of one SocketServer istance, you can specify the parameter dqmqueue, in order to send the task to another queue, like below:

	specific_queue = DQMQueue.objects.get(description='foo_queue')
    push_task_to_queue(send_mail,subject="foo",message="baz",recipient_list=[user.email], dqmqueue=specific_queue)

### Components:

1. Python SocketServer that listens to a tcp socket.
2. A Worker thread.
3. A python Queue

### Workflow:

The workflow that runs an async task:

1. When ``SocketServer`` starts, it initializes the ``Worker`` thread.
2. ``SocketServer`` listens to requests.
3. When ``SocketServer`` receives a request - a callables with args and kwargs - it puts the request on a python ``Queue``.
4. The ``Worker`` thread picks a task from the ``Queue``.
5. The ``Worker`` thread runs the task.


### Can this queue scale to production?:

Absolutely!: SocketServer is simple, but solid, and as the
site gets more traffic, it's possible to move the django-queue-manager server to
another machine, separate database, use multiple istance of SocketServer, etc...
At some point, probably, it's better to pick Celery. Until then, django-queue-manager is a simple, solid, and
no-hustle solution.


## <a name="Install"></a>Install:

1. Install the django-queue-manager with the following pip command ``pip3 install django-queue-manager``.

2. Add ``django-queue-manager`` in the ``INSTALLED_APPS`` list.

3. Migrate:

       $ manange.py migrate

4. The django-queue-manager app has an API module, with a ``push_task_to_queue``
   function. Use this function to send callables with args and kwargs to the queue,
   you can specify a specific queue with the parameter dqmqueue or use the default one if none it's specified, for the async run.

## <a name="Settings"></a>Settings:


To change the default django-queue-manager settings, you can modify the backend default queue present in the django admin pages.

In a glance, the queue, has the following parameters:

**description** The description of the queue.

**queue\_host** The host to run the SocketServer. The default is
'localhost'. (It can be also a remote host)

**queue\_port**
The port that SocketServer listens to. The default is
8002.

**max\_retries** The number of times the Worker thread will try to run a
task before skipping it. The default is 3.


So, in a nutshell, for using multiple queues, simply add a new queue
in the admin page and pass the istance of a valid ``DQMQueue`` object in the function like below:



    from mysite.django-queue-manager.API import push_task_to_queue
    ...
	specific_queue = DQMQueue.objects.get(description='foo_queue')
    push_task_to_queue(send_mail,subject="foo",message="baz",recipient_list=[user.email], dqmqueue=specific_queue)


## <a name="Run-the-Tasks-Queue-Server"></a>Run the Tasks Queue Server:


### Start the Server:

From shell or a process control system, run the following script with python >= 3
(if you use a VirtualEnv, specify the environment path in supervisor conf.d file):



    import os
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "YOUR-APP-NAME.settings")
	import django
	django.setup()
	import time
	from django_queue_manager import worker_manager
	from django_queue_manager.models import DQMQueue
	from django_queue_manager.server_manager import TaskSocketServerThread
	worker_manager.start()
	server_thread = TaskSocketServerThread('localhost', DQMQueue.objects.first().queue_port)
	time.sleep(5)
	socket_server = server_thread.socket_server()
	socket_server.serve_forever()


*Note: You have to change the variable "YOUR-APP-NAME.settings" with the
name of your app, like that: "email_sender.settings")*


### The Shell interface:


Django-queue-manager, provides a simple script called ``shell.py``
that it's useful in order to see how the queue, worker and server it's going on,
the base syntax it's really simple



    $ python <package-install-dir>/shell.py queue-host queue-port command

### Stop the server:

To stop the worker thread gracefully:



    $ python django-queue-manager/shell.py localhost 8002 stop
    Sent: ping
    Received: (False, 'Worker Off')

This will send a stop event to the Worker thread. Check that the Worker
thread stopped:



    $ python django-queue-manager/shell.py localhost 8002 ping
    Sent: ping
    Received: (False, 'Worker Off')

Now you can safely stop SocketServer:



    $ ps ax | grep django-queue-manager
    12345 pts/1 S 7:20 <process name>
    $ sudo kill 12345

### Ping the server:
From shell:

    $ python django-queue-manager/shell.py localhost 8002 ping
    Sent: ping
    Received: (True, "I'm OK")

### Tasks that are waiting on the Queue:

From shell:

    $ python django-queue-manager/shell.py localhost 8002 waiting
    Sent: waiting
    Received: (True, 115)

115 tasks are waiting on the queue

### Count total tasks handled to the Queue

From shell:



    $ python django-queue-manager/shell.py localhost 8002 handled
    Sent: handled
    Received: (True, 862)

Total of 862 tasks were handled to the Queue from the moment the thread
started

*Note: If you use the tasks server commands a lot, add shell aliases for
these commands*




## <a name="Persistency"></a>Persistency:

### *Tasks are saved in the database: why not! you already have a DB!*

**QueuedTasks** The model saves every tasks pushed to the queue and not yet processed.
The task is pickled as a ``django-queue-manager.task_manager.Task`` object, which is a
simple class with a ``callable``, ``args``, ``dqmqueue`` and ``kwargs`` attributes,
and one method: ``run()``. 

*After a successful execution, the QueuedTasks will be deleted and moved into the ``SuccessTask`` queue.*

*Note: If you use the requeue task function in the django admin dropdown action, the
selected tasks will be requeued like NEW TASKS (with a new ``task_id``) in the ``QueuedTasks`` table.*

**SuccessTasks** The Worker thread saves to this model the successfully executed job
with all informations like above:

``task_function_name``: The complete function name like "module.function_name"

``task_args``: The variable list arguments in plain text

``task_kwargs``: The dictionary arguments in plain text

``task_id``: The task id carried from the initial QueuedTask istance

``success_on``: The success datetime

``pickled_task``: The complete pickled task

``dqmqueue``: The reference of the dqmqueue queue istance

**FailedTasks** After the Worker tries to run a task several times
according to ``max_retries``(specified in the dqmqueue used), and the task still fails, the Worker saves it to this model with all informations like above:

``task_function_name``: The complete function name like "module.function_name"

``task_args``: The variable list arguments in plain text

``task_kwargs``: The dictionary arguments in plain text

``task_id``: The task id carried from the initial QueuedTask istance

``failed_on``: The last failed run datetime

``exception``: The exception message, only the exception from the last run is saved.

``pickled_task``: The complete pickled task

``dqmqueue``: The reference of the dqmqueue queue istance

*Note: If you use the requeue task function in the django admin dropdown action, the
selected tasks will be requeued like NEW TASKS (with a new ``task_id``) in the ``QueuedTasks`` table.*

### Purge Tasks:

According to your project needs, you can purge tasks using the django admin
interface or manually with a query execution.

In a similar way, delete the failed/success tasks. You can run a cron script, or
other script, to purge the tasks.

### Connections:

If most of the tasks require a specific connection, such as SMTP or a
database, you can subclass (...or edit directly) the Worker class and add a ping or other check
for this connection **before** the tasks runs. If the connection is
not avaialable, just try to re-connect.

Otherwise the Worker will just run and fail a lot of tasks.

<a name="Run-the-Tasks-Queue-on-Another-Server"></a>Run the Tasks Queue on Another Server:
-------------------------------------

The same ``django-queue-manager`` app can run from another server, and provide a
seprate server queue for the async tasks.

Here is a simple way to do it:

1. The queue server should be similar to the main django server, just
   without a webserver.
2. Deploy your django code to these two remotes: the main with the
   web-server, and the queue server
3. Open firewalls ports between the main django server, and the queue
   server, and between the main django database and the queue server host
4. On the django main server, change the host and port details directly from the admin site.

That's it!
For any support/issue request, contact the author: fardella.simone@gmail.com
