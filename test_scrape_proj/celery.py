import os

from celery import Celery

from test_scrape_proj import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_scrape_proj.settings')

app = Celery('test_scrape_proj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = True

app.conf.beat_schedule = {
    "usd_rate": {
        "task": "currencies.tasks.periodic_usd_rate",
        "schedule": 30.0,
    },
}

app.conf.beat_schedule = {
    "sync_markets": {
        "task": "marketplaces.tasks.periodic_sync_markets",
        "schedule": 30.0,
    }
}
