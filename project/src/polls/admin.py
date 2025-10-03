"""
Admin configuration for the Poll, Choice and Vote model.
Registration of these models in the Django admin panel,
allowing administrators to manage them through the built-in admin interface.
"""


from django.contrib import admin
from django.utils import timezone
from django.db.models import Count

from .models import Choice, Poll, Vote


class ChoiceInline(admin.TabularInline):
    """
    Inline for displaying and editing choices directly from poll.
    """
    model = Choice
    extra = 2
    readonly_fields = ['vote_count']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_vote_count=Count('choice_votes'))

    def vote_count(self, obj):
        """
        Returns the number of votes for given choice.
        """
        return obj._vote_count
    vote_count.short_description = 'Liczba głosów'


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = [
        'question',
        'creation_date',
        'end_date',
        'total_votes',
        'archive_date',
    ]
    list_filter = ['creation_date', 'end_date']
    readonly_fields = ['creation_date']
    actions = [
        'archive_selected',
        'unarchive_selected',
    ]
    list_editable = ['archive_date']

    inlines = [ChoiceInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_total_votes=Count('poll_votes'))

    def total_votes(self, obj):
        """
        Method getting total votes for a poll.
        """
        return obj._total_votes
    total_votes.short_description = 'Łączne głosy'

    def archive_selected(self, request, queryset):
        """
        Sets the poll status to archived.
        Updates 'archive_date' only.
        """
        queryset.update(archive_date=timezone.now())
    archive_selected.short_description = 'Archiwizuj wybrane ogłoszenia'

    def unarchive_selected(self, request, queryset):
        """
        Sets the poll status to unarchived.
        Updates 'archive_date' only
        """
        queryset.update(archive_date=None)
    unarchive_selected.short_description = 'Odarchiwizuj wybrane ankiety'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text',
                    'poll',
                    'vote_count']
    list_filter = ['poll']
    readonly_fields = ['poll']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_vote_count=Count('choice_votes'))

    def vote_count(self, obj):
        """
        Method getting vote count for a choice
        """
        return obj._vote_count
    vote_count.short_description = 'Liczba głosów'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'poll',
                    'choice',
                    'vote_date']
    list_filter = ['poll',
                   'vote_date']
    readonly_fields = ['user',
                       'poll',
                       'choice',
                       'vote_date']
    search_fields = ['user__username']
