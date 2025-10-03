"""
Urls for galleries and photos operations - showing gallery list for specific user,
editing, deleting user's galleries/photos and adding new galleries/photos.
Directs users to the appropriate page where they can perform the activity they are interested in.
"""
from django.urls import path
from . import views


app_name = 'photo_gallery'

urlpatterns = [
    path('', views.GalleryListView.as_view(), name='gallery_list', kwargs={'filter': 'all'}),
    path('my-galleries/', views.GalleryListView.as_view(), name='user_gallery_list', kwargs={'filter': 'my'}),
    path('create/', views.GalleryCreateView.as_view(), name='gallery_create'),
    path('<slug:slug>/', views.GalleryDetailView.as_view(), name='gallery_detail'),
    path('<slug:slug>/edit/', views.GalleryUpdateView.as_view(), name='gallery_update'),
    path('<slug:slug>/delete/', views.GalleryDeleteView.as_view(), name='gallery_delete'),
    path('<slug:slug>/add-photo/', views.PhotoCreateView.as_view(), name='photo_add'),
    path('<slug:slug>/photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('<slug:slug>/photo/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo_update'),
    path('<slug:slug>/photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
]