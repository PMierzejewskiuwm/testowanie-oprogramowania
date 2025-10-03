"""
Admin configuration for the Event model.
Registration of Event model in the Django admin panel,
allowing administrators to manage events through the built-in admin interface.
"""

from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name',
                    'event_date',
                    'location',
                    'description',
                    'image',
                    'created_at',
                    'updated_at',
                    'creator',
                    'is_verified',
                    'is_pinned',
                    'is_archived'
                    )
    list_editable = ['is_verified', 'is_pinned', 'is_archived']
    actions = ['verify_selected', 'archive_selected']

    def verify_selected(self, request, queryset):
        queryset.update(is_verified=True)
    verify_selected.short_description = "Zaznacz jako zweryfikowane"

    def archive_selected(self, request, queryset):
        queryset.update(is_archived=True)
    archive_selected.short_description = 'Archiwizuj wybrane wydarzenia'