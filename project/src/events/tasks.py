from celery import shared_task
from django.utils import timezone
from .models import Event

@shared_task
def archive_past_events():
    """Task to archive all past events."""
    Event.objects.filter(
        event_date__lt=timezone.now(),
        is_archived=False
    ).update(is_archived=True)