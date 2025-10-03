from django.urls import path
from .views import (
    UserProfileView,
    UserProfileUpdateView,
    AccountSettingsView,
    UserPasswordChangeView,
    UserEmailChangeView,
    UsernameChangeView
)

app_name = 'user_profile'

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
    path('edit/', UserProfileUpdateView.as_view(), name='profile_edit'),
    path('settings/', AccountSettingsView.as_view(), name='account_settings'),
    path('settings/password/', UserPasswordChangeView.as_view(), name='password_change'),
    path('settings/email/', UserEmailChangeView.as_view(), name='email_change'),
    path('settings/username/', UsernameChangeView.as_view(), name='username_change'),
]