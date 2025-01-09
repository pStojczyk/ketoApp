"""
This file contains the setup and configuration for Celery in ketoApp project, including the creation of the Celery
application instance, loading configuration from Django settings, and discovering tasks automatically from Django apps.
"""

import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ketoApp.settings')

app = Celery('ketoApp', broker="redis://localhost:6379", backend="redis://localhost:6379")

app.conf.broker_connection_retry_on_startup = True

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    This task is related to the current request and is used for inspecting Celery task requests during development.

    Args:
        self: The current task instance.

    Prints:
        The task request information for debugging.
    """

    print(f'Request: {self.request!r}')
