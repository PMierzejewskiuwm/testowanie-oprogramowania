from django import template
import random
from django.db.models import Count
from polls.models import Poll

register = template.Library()

@register.inclusion_tag('includes/random_poll.html')
def random_poll():
    """
    Method getting random poll with its total votes,
    vote percentages. Only polls that have total votes
    greater than 1 and no archive date are chosen
    """
    queryset = (
        Poll.objects
            .annotate(num_votes=Count('poll_votes'))
            .filter(archive_date__isnull=True)
    )

    polls_list = list(queryset)
    if not polls_list:
        return {'poll': None, 'choices': None, 'total_votes': 0}

    poll = random.choice(polls_list)

    choices_queryset = poll.choices.annotate(votes_count=Count('choice_votes'))
    total_votes = poll.total_votes()

    for choice in choices_queryset:
        if total_votes:
            choice.percentage = round((choice.votes_count / total_votes) * 100, 1)
        else:
            choice.percentage = 0.0

    return {
        'poll': poll,
        'choices': choices_queryset,
        'total_votes': total_votes,
    }