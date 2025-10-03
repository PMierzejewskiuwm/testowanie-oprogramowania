"""
Urls for user registration, login, logout and pages related to password reset.
Directs users to the appropriate page where they can perform the activity they are interested in.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView, LoginView, CustomLogoutView

app_name = "users"

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url='/users/password-reset/done/'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url='/users/password-reset/complete/'
    ), name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),

]

