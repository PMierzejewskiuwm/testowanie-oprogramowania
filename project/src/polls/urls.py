from django.urls import path

from . import views
from .views import (PollArchiveView, PollCreateView, PollDeleteView,
                    PollDetailView, PollListView, PollResultsView)

app_name = 'polls'

urlpatterns = [
    path(
        'user_poll_list',
        PollListView.as_view(),
        {'filter': 'my'},
        name='user_poll_list',
    ),
    path(
        '',
        PollListView.as_view(),
        {'filter': 'all_non_archived'},
        name="list_poll",
    ),
    path(
        'list_archived_poll',
        PollListView.as_view(),
        {'filter': 'all_archived'},
        name='list_archived_poll',
    ),
    path(
        'poll_detail/<int:pk>/',
        PollDetailView.as_view(),
        name='poll_detail'
    ),
    path(
        'poll_results/<int:pk>/',
        PollResultsView.as_view(),
        name='poll_results',
    ),
    path('create_poll/',
         PollCreateView.as_view(),
         name='create_poll'),
    path(
        'delete_poll/<int:pk>/',
        PollDeleteView.as_view(),
        name='delete_poll'
    ),
    path(
        'archive_poll/<int:pk>/',
        views.PollArchiveView.as_view(),
        name='archive_poll',
    ),
]
