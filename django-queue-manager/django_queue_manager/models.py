from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class DQMQueue(models.Model):
    description = models.CharField(max_length=255)
    queue_host = models.CharField(max_length=255)
    queue_port = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    max_retries = models.PositiveSmallIntegerField()

    def __str__(self):
        return "Queue Description: {description} -> Queue Host: {host} -> Queue Port: {port} -> Max Retries: {max_retries}".format(
            description=self.description,
            host=self.queue_host,
            port=self.queue_port,
            max_retries=self.max_retries)

    class Meta:
        verbose_name = 'DQMQueue'
        verbose_name_plural = 'DQMQueues'


# Create your models here.
class QueuedTasks(models.Model):
    task_function_name = models.TextField()
    task_args = models.TextField()
    task_kwargs = models.TextField()
    pickled_task = models.BinaryField()
    queued_on = models.DateTimeField(auto_now_add=True)
    dqmqueue = models.ForeignKey(DQMQueue, on_delete=models.CASCADE)

    def __str__(self):
        return "Job-Id: {job_id} -> Queued on: {queued_on} -> Queue: {queue}".format(
            job_id=self.pk,
            queued_on=self.queued_on, queue=self.dqmqueue.description)

    class Meta:
        verbose_name = 'Queued Task'
        verbose_name_plural = 'Queued Tasks'


class SuccessTasks(models.Model):
    task_function_name = models.TextField()
    task_args = models.TextField()
    task_kwargs = models.TextField()
    task_id = models.IntegerField()
    success_on = models.DateTimeField(auto_now_add=True)
    pickled_task = models.BinaryField()
    dqmqueue = models.ForeignKey(DQMQueue, on_delete=models.CASCADE)

    def __str__(self):
        return "Job-Id: {job_id} -> Success on: {success_on} -> Queue: {queue}".format(
            job_id=self.task_id,
            success_on=self.success_on, queue=self.dqmqueue.description)

    class Meta:
        verbose_name = 'Success Task'
        verbose_name_plural = 'Success Tasks'


class FailedTasks(models.Model):
    task_function_name = models.TextField()
    task_args = models.TextField()
    task_kwargs = models.TextField()
    task_id = models.IntegerField()
    exception = models.TextField()
    failed_on = models.DateTimeField(auto_now_add=True)
    pickled_task = models.BinaryField()
    dqmqueue = models.ForeignKey(DQMQueue, on_delete=models.CASCADE)

    def __str__(self):
        return "Job-Id: {job_id} -> Failed on: {failed_on} -> Queue: {queue}".format(
            job_id=self.task_id,
            failed_on=self.failed_on, queue=self.dqmqueue.description)

    class Meta:
        verbose_name = 'Failed Task'
        verbose_name_plural = 'Failed Tasks'
