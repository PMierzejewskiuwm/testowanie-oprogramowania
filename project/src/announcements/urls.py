from django.urls import path

from . import views

app_name = 'announcements'

urlpatterns = [
    path(
        'user_announcement_list',
        views.AnnouncementListView.as_view(),
        {'filter': 'my'},
        name='user_announcement_list',
    ),
    path(
        'list_announcement',
        views.AnnouncementListView.as_view(),
        {'filter': 'all_non_archived'},
        name='list_announcement',
    ),
    path(
        'list_archived_announcement',
        views.AnnouncementListView.as_view(),
        {'filter': 'all_archived'},
        name='list_archived_announcement',
    ),
    path(
        'announcement_detail/<int:pk>/',
        views.AnnouncementDetailView.as_view(),
        name='announcement_detail',
    ),
    path(
        'create_announcement/',
        views.AnnouncementCreateView.as_view(),
        name='create_announcement',
    ),
    path(
        'edit_announcement/<int:pk>/',
        views.AnnouncementUpdateView.as_view(),
        name='edit_announcement',
    ),
    path(
        'delete_announcement/<int:pk>/',
        views.AnnouncementDeleteView.as_view(),
        name='delete_announcement',
    ),
    path(
        'archive_announcement_toggle/<int:pk>/',
        views.AnnouncementToggleArchiveView.as_view(),
        name='archive_announcement_toggle',
    ),
]
