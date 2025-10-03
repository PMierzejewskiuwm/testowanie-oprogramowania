"""
Admin configuration for the CustomUser model.
Registration of CustomUser model in the Django admin panel,
allowing administrators to manage user accounts through the built-in admin interface.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)
