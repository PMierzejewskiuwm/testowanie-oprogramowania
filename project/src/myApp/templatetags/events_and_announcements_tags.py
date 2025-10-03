from django import template
from events.models import Event
from announcements.models import Announcement

register = template.Library()

@register.inclusion_tag('includes/latest_events.html')
def latest_events(limit=5):
    events = Event.objects.filter(is_verified=True).order_by('-created_at')[:limit]
    return {'events': events}


@register.inclusion_tag('includes/latest_announcements.html')
def latest_announcements(limit=5):
    announcements = Announcement.objects.filter(is_verified=True).order_by('-date')[:limit]
    return {'announcements': announcements}


@register.inclusion_tag('includes/top_rated_events.html')
def top_rated_events(limit=5):
    events = Event.objects.filter(is_verified=True)
    events_with_ratings = []

    for event in events:
        avg_rating = event.average_rating
        if avg_rating is not None:
            events_with_ratings.append({'event': event, 'rating': avg_rating})

    events_with_ratings.sort(key=lambda x: x['rating'], reverse=True)

    return {'events': events_with_ratings[:limit]}


@register.inclusion_tag('includes/top_rated_announcements.html')
def top_rated_announcements(limit=5):
    announcements = Announcement.objects.filter(is_verified=True)
    announcements_with_ratings = []

    for announcement in announcements:
        avg_rating = announcement.average_rating
        if avg_rating is not None:
            announcements_with_ratings.append({'announcement': announcement, 'rating': avg_rating})

    announcements_with_ratings.sort(key=lambda x: x['rating'] or 0, reverse=True)

    return {'announcements': announcements_with_ratings[:limit]}
