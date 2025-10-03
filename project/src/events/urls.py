"""
Urls for events operations - showing event list for specific user, editing, deleting user's events and adding new events.
Directs users to the appropriate page where they can perform the activity they are interested in.
"""

from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path('user_event_list/', views.EventListView.as_view(), {'filter': 'my'}, name='user_event_list'),
    path('event_list/', views.EventListView.as_view(), {'filter': 'all_non_archived'}, name='list_event'),
    path('events/archive/', views.EventListView.as_view(), {'filter': 'all_archived'}, name='list_archived_event'),
    path('create_event/', views.EventCreateView.as_view(), name='create_event'),
    path('edit_event/<int:pk>/', views.EventUpdateView.as_view(), name='edit_event'),
    path('delete_event/<int:pk>/', views.EventDeleteView.as_view(), name='delete_event'),
    path('event_detail/<int:pk>/', views.EventDetailView.as_view(), name='detail_event'),
]
