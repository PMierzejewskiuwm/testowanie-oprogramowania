"""
Urls for comments and ratings operations - adding rating, comments and replies,
editing existing comments (or replIes), deleting  comments or replies and ratings.
Directs users to the appropriate page where they can perform the activity they are interested in.
"""
from django.urls import path

from .models import Comment, Rating
from .views import (
    AddRatingView,
    AddCommentView,
    AddReplyView,
    DeleteRatingOrCommentView,
    EditCommentView,
)

app_name = "comments_and_ratings"

urlpatterns = [
    path(
        '<str:app_label>/<str:model_name>/<int:object_id>/rate/',
        AddRatingView.as_view(),
        name='add_rating',
    ),
    path(
        '<str:app_label>/<str:model_name>/<int:object_id>/comment/',
        AddCommentView.as_view(),
        name='add_comment',
    ),
    path(
        'comment/<int:comment_id>/reply/',
        AddReplyView.as_view(),
        name='add_reply',
    ),
    path(
        'comment/<int:pk>/edit/',
        EditCommentView.as_view(),
        name='edit_comment',
    ),
    path(
        'delete/comment/<int:pk>/',
        DeleteRatingOrCommentView.as_view(
            model=Comment,
            success_message="Komentarz został usunięty!",
            is_comment=True,
        ),
        name='delete_comment',
    ),
    path(
        'delete/rating/<int:pk>/',
        DeleteRatingOrCommentView.as_view(
            model=Rating,
            success_message="Ocena została usunięta!",
            is_comment=False,
        ),
        name='delete_rating',
    ),
]