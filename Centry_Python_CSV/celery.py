import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
from csvInfoRetriever.config import PRICES_UPDATE_TIME, STOCKS_UPDATE_TIME

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Centry_Python_CSV.settings')

app = Celery('csvInfoRetriever')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'centry_stock_save-crontab': {
        'task': 'csvInfoRetriever.tasks.centry_stock_save',
        'schedule': PRICES_UPDATE_TIME,
        'args': [],
    },
    'centry_price_save-crontab': {
        'task': 'csvInfoRetriever.tasks.centry_price_save',
        'schedule': STOCKS_UPDATE_TIME,
        'args': [],
    }
}
