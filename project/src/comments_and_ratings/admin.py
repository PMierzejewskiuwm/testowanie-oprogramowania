"""
Admin configuration for the Rating and Comment models.
Registration of Rating and Comment models in the Django admin panel,
allowing administrators to manage comments/ratings through the built-in admin interface.
"""

from django.contrib import admin
from .models import Rating, Comment


@admin.register(Rating)
class EventAdmin(admin.ModelAdmin):
    list_display = ('content_type',
                    'object_id',
                    'user',
                    'rating',
                    'created_at',
                    'updated_at')


@admin.register(Comment)
class EventAdmin(admin.ModelAdmin):
    list_display = ('content_type',
                    'object_id',
                    'user',
                    'parent_comment',
                    'content',
                    'created_at',
                    'updated_at',
                    'is_active')

    list_editable = ('is_active',)
