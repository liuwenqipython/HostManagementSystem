import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HostManagementSystem.settings')

app = Celery('host_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from hosts.tasks import change_host_passwords_task, daily_statistics_task

    sender.add_periodic_task(
        8 * 60 * 60,
        change_host_passwords_task.s(),
        name='Change host passwords every 8 hours',
    )

    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        daily_statistics_task.s(),
        name='Daily host statistics at midnight',
    )
