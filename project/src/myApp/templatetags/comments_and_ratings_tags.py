from django import template
from django.contrib.contenttypes.models import ContentType
from comments_and_ratings.models import Rating, Comment
from django.db.models import Avg

register = template.Library()


@register.inclusion_tag('comments_and_ratings/rating_form.html')
def rating_form(obj, user):
    """
    Renders the rating form for a given object and user.
    This inclusion tag:
    - Retrieves the user's current rating for the object, if it exists.
    - Computes the average rating and the number of ratings for the object.
    - Passes the content type, object ID, and rating data to the template.
    """
    content_type = ContentType.objects.get_for_model(obj)

    user_rating = None
    user_rating_id = None
    if user.is_authenticated:
        try:
            rating = Rating.objects.get(
                content_type=content_type,
                object_id=obj.id,
                user=user
            )
            user_rating = rating.rating
            user_rating_id = rating.id
        except Rating.DoesNotExist:
            pass

    average_rating = Rating.objects.filter(
        content_type=content_type,
        object_id=obj.id
    ).aggregate(Avg('rating'))['rating__avg']

    return {
        'content_type': content_type,
        'user_rating_id': user_rating_id,
        'object_id': obj.id,
        'user_rating': user_rating,
        'average_rating': round(average_rating, 1) if average_rating else None,
        'ratings_count': Rating.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).count(),
        'user': user
    }


@register.inclusion_tag('comments_and_ratings/comment_list.html')
def comment_list(obj, user):
    """
    Renders a list of top-level comments for a given object.
    This inclusion tag:
    - Retrieves all top-level (non-reply) comments related to the object.
    - Passes the comments along with the content type and object ID to the template.
    """
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        parent_comment__isnull=True
    ).order_by('-created_at')

    return {
        'content_type': content_type,
        'object_id': obj.id,
        'comments': comments,
        'user': user
    }


@register.simple_tag
def get_ratings_count(obj):
    """Returns the number of ratings associated with a given object"""
    content_type = ContentType.objects.get_for_model(obj)
    return Rating.objects.filter(
        content_type=content_type,
        object_id=obj.id
    ).count()


@register.simple_tag
def get_comments_count(obj):
    """Returns the number of comments associated with a given object."""
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id
    ).count()