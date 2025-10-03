from celery import shared_task
from django.utils import timezone

from .models import Poll


@shared_task
def archive_past_polls():
    """Task to archive all polls after end_date is reached."""
    Poll.objects.filter(
        end_date__lt=timezone.now(),
        archive_date__isnull=True
    ).update(archive_date=timezone.now())
