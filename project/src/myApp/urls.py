"""
URL configuration for myApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import HomeView
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='homepage'),
    path('kontakt/', include('kontakt.urls')),
    path('users/', include('users.urls')),
    path('announcements/', include('announcements.urls')),
    path('events/', include('events.urls')),
    path('user_profile/', include('user_profile.urls')),
    path('photo_gallery/', include('photo_gallery.urls')),
    path('o-nas/', views.about, name='about'),
    path('uslugi-platne/', views.paid_service, name='paid_service'),
    path('informacje-pomoc/', views.info_help, name='info_help'),
    path('comments_and_ratings/', include('comments_and_ratings.urls')),
    path('polls/', include('polls.urls'))
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)