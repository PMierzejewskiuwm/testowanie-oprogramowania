"""
Admin configuration for the UserProfile model.
Registration of Event model in the Django admin panel,
allowing administrators to manage events through the built-in admin interface.
"""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class EventAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'description',
                    'birth_date',
                    'profile_picture',
                    'phone_number')
