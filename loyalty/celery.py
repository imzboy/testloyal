from datetime import datetime, timezone
import os

from celery import Celery

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loyalty.settings')

app = Celery('loyalty')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task
def expire_cards():
    from .models import Card
    from loyalty.models import CardStatus

    will_be_expired_cards = Card.objects.filter(
        expires_at__lt=datetime.now(tz=timezone.utc),
        status__in=[CardStatus.ACTIVE.value, CardStatus.INACTIVE.value]
    ).update(status=CardStatus.EXPIRED.value)

    log.info(f'Expired {will_be_expired_cards} cards')
