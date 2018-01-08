from django.contrib import admin

# Register your models here.
from django_queue_manager.models import *
from django_queue_manager.task_manager import TaskManager


def requeue_task(modeladmin, request, queryset):
    for task in queryset:
        TaskManager.requeue_task(task)

def retry_task(modeladmin, request, queryset):
    for task in queryset:
        TaskManager.retry_failed_task(task)

class QueuedModelAdmin(admin.ModelAdmin):
    readonly_fields = ('task_function_name','task_args', 'task_kwargs','pickled_task', 'dqmqueue', 'queued_on', )

    actions = [requeue_task]

    def has_add_permission(self, request):
        return False

class SuccessModelAdmin(admin.ModelAdmin):
    readonly_fields = ('task_function_name', 'task_args', 'task_kwargs','task_id', 'pickled_task', 'dqmqueue', 'success_on', )

    def has_add_permission(self, request):
        return False

class FailedModelAdmin(admin.ModelAdmin):
    readonly_fields = ('task_function_name', 'task_args', 'task_kwargs','task_id', 'pickled_task', 'failed_on', 'dqmqueue', 'exception', )

    actions = [retry_task]

    def has_add_permission(self, request):
        return False

admin.site.register(DQMQueue)
admin.site.register(QueuedTasks, QueuedModelAdmin)
admin.site.register(SuccessTasks, SuccessModelAdmin)
admin.site.register(FailedTasks, FailedModelAdmin)