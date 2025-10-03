from django.contrib import admin
from django.utils import timezone

from .models import Announcement


# Register your models here.
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'place',
        'rooms',
        'price',
        'date',
        'description',
        'banner',
        'creator',
        'is_verified',
        'is_pinned',
        'archive_date'
    )

    list_filter = ['archive_date']
    list_editable = ['is_verified', 'is_pinned']
    actions = ['archive_selected',
               'unarchive_selected',
               'verify_selected',
               'hide_selected',
               ]

    def archive_selected(self, request, queryset):
        """
        Sets the announcement status to archived.
        Updates 'archive_date' only.
        """
        queryset.update(archive_date=timezone.now())
    archive_selected.short_description = 'Archiwizuj wybrane ogłoszenia'

    def unarchive_selected(self, request, queryset):
        """
        Sets the announcement status to unarchived.
        Updates 'archive_date' only
        """
        queryset.update(archive_date=None)
    unarchive_selected.short_description = 'Odarchiwizuj wybrane ogłoszenia'

    def verify_selected(self, request, queryset):
        """
        Verifies announcements made by non logged-in users.
        Updates is_verified only.
        """
        queryset.update(is_verified=True)
    verify_selected.short_description = 'Zweryfikuj ogłoszenia'

    def hide_selected(self, request, queryset):
        """
        Uses is_verified to hide announcements.
        Updates is_verified only.
        """
        queryset.update(is_verified=False)
    hide_selected.short_description = 'Ukryj ogłoszenia'
