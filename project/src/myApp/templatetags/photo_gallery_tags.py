from django import template
import random
from photo_gallery.models import Photo, Gallery

register = template.Library()


@register.inclusion_tag('includes/random_gallery_photo.html')
def random_gallery_photo():
    photos = list(Photo.objects.all())
    photo = random.choice(photos) if photos else None
    return {'photo': photo}

@register.inclusion_tag('includes/latest_galleries.html')
def latest_galleries(limit=5):
    galleries = Gallery.objects.order_by('-created_at')[:limit]
    return {'galleries': galleries}


@register.inclusion_tag('includes/top_rated_galleries.html')
def top_rated_galleries(limit=5):
    galleries = Gallery.objects.all()
    galleries_with_ratings = []

    for gallery in galleries:
        avg_rating = gallery.average_rating
        if avg_rating is not None:
            galleries_with_ratings.append({'gallery': gallery, 'rating': avg_rating})

    galleries_with_ratings.sort(key=lambda x: x['rating'] or 0, reverse=True)

    return {'galleries': galleries_with_ratings[:limit]}
