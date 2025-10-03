from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.db import models

from comments_and_ratings.models import Rating
from myApp.utils.upload_pather import dynamic_image_upload_pather


class Event(models.Model):
    """
    A model representing an event in the system.

    Attributes:
        event_name (CharField): Name of the event (max 100 characters)
        event_date (DateTimeField): Date and time of the event
        city (CharField): Map where the event is taking place (max 100 characters)
        location (CharField): Location of the event (max 100 characters)
        description (TextField): Description of the event (max 500 characters)
        creator (ForeignKey): Creator of the event (associated with the user model)
                              Can be None for events with anonymous creators
    """
    event_name = models.CharField(max_length=100, verbose_name="nazwa wydarzenia")
    event_date = models.DateTimeField(verbose_name="data wydarzenia")
    location = models.CharField(max_length=100, verbose_name="miasto wydarzenia")
    city = models.PointField(help_text = "<br>", verbose_name="miejsce wydarzenia", null=True, blank=True)
    description = models.TextField(max_length=500, verbose_name="opis wydarzenia")
    image = models.ImageField(
        upload_to=dynamic_image_upload_pather,
        blank=True,
        verbose_name="zdjęcie wydarzenia",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="data stworzenia wydarzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="data edycji wydarzenia")
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="twórca wydarzenia"
    )
    is_archived = models.BooleanField(default=False, verbose_name="czy archiwalne")
    is_verified = models.BooleanField(default=False, verbose_name="czy zweryfikowane")
    is_pinned = models.BooleanField(default=False, verbose_name="czy przypięte")

    ratings = GenericRelation('comments_and_ratings.Rating')
    comments = GenericRelation('comments_and_ratings.Comment')

    class Meta:
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"

    def get_creator_name(self):
        """
        Returns the name of the event creator, or 'anonim' if the creator is not specified.

        Returns:
            str: Username or 'anonim'
        """
        return self.creator.username if self.creator else "anonim"

    def get_absolute_url(self):
        return reverse('events:detail_event', kwargs={'pk': self.pk})

    def __str__(self):
        """
        Returns the string representation of the event, which is the event name.
        """
        return self.event_name

    @property
    def average_rating(self):
        result = self.ratings.aggregate(models.Avg('rating'))
        return round(result['rating__avg'], 1) if result['rating__avg'] else None

    def get_user_rating(self, user):
        try:
            return self.ratings.get(user=user).rating
        except Rating.DoesNotExist:
            return None

