"""
Admin configuration for the Gallery and Photo models.
Registration of Gallery and Photo models in the Django admin panel,
allowing administrators to manage galleries/photos through the built-in admin interface.
"""

from django.contrib import admin
from .models import Gallery, Photo


@admin.register(Gallery)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'description',
                    'created_at',
                    'updated_at',
                    'creator',
                    'thumbnail',
                    'slug')

@admin.register(Photo)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'image',
                    'description',
                    'uploaded_at')
