from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone

from comments_and_ratings.models import Rating
from myApp.utils.upload_pather import dynamic_image_upload_pather


# Create your models here.
class Announcement(models.Model):
    """
    A model representing an announcement in the system.

    Attributes:
        - title (CharField): Name of the announcement (max 50 characters).
        - place (CharField): Place announcement mentions (max 50 characters).
        - rooms (PositiveIntegerField): Amount of rooms available.
        - price (DecimalField): Price mentioned in the announcement
        - (max 10 digits).
        - date (DateTimeField): The date of announcement creation.
        - description (TextField): The description of the announcement.
        - banner (ImageField): Image of the announcement.
        - creator (ForeignKey): Creator of the announcement
        (associated with the user model). Can be None for
        announcements with anonymous creators
        - archive_date (DateTimeField): Date and time of archivization
        - is_verified (BooleanField): Information whether announcement is
        verified
    """

    title = models.CharField(max_length=50, verbose_name="tytuł ogłoszenia")
    place = models.CharField(max_length=50,
                             verbose_name="miejsce z ogłoszenia")
    rooms = models.PositiveIntegerField(verbose_name="ilość pokoi")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="cena wynajmu"
    )
    date = models.DateTimeField(
        auto_now_add=True, verbose_name="data utworzenia ogłoszenia"
    )
    description = models.TextField(verbose_name="opis ogłoszenia")
    banner = models.ImageField(
        upload_to=dynamic_image_upload_pather,
        blank=True,
        verbose_name="zdjęcie ogłoszenia",
    )
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="twórca ogłoszenia",
    )
    archive_date = models.DateTimeField(
        null=True, blank=True, verbose_name="data archiwizacji"
    )
    is_verified = models.BooleanField(default=False,
                                      verbose_name="status weryfikacji")
    is_pinned = models.BooleanField(default=False, verbose_name="czy przypięte")

    ratings = GenericRelation('comments_and_ratings.Rating')
    comments = GenericRelation('comments_and_ratings.Comment')

    def archive_announcement(self):
        """
        Sets the announcement status to archived.
        Updates 'archive_date' only
        """
        self.archive_date = timezone.now()
        self.save(update_fields=["archive_date"])

    def unarchive_announcement(self):
        """
        Sets the announcement status to unarchived.
        Updates 'archive_date' only
        """
        self.archive_date = None
        self.save(update_fields=["archive_date"])

    def get_creator_name(self):
        """
        Returns the name of the announcement's creator, or 'anonim'
        if the creator is not specified.

        Returns:
            str: Username or 'anonim'
        """
        return self.creator.username if self.creator else "anonim"

    def get_archive_date(self):
        """
        Returns the date announcement was archived or '-'
        if the date is not specified.

        Returns:
            datetime: archive_date
            str: '-' if there is no archive_data
        """
        return self.archive_date if self.archive_date else "-"

    def get_absolute_url(self):
        return reverse('announcements:announcement_detail', kwargs={'pk': self.pk})

    def __str__(self):
        """
        Returns the string representation of the announcement,
        which is the title.
        """
        return self.title

    class Meta:
        verbose_name = "ogłoszenie"
        verbose_name_plural = "ogłoszenia"

    @property
    def average_rating(self):
        result = self.ratings.aggregate(models.Avg('rating'))
        return round(result['rating__avg'], 1) if result['rating__avg'] else None

    def get_user_rating(self, user):
        try:
            return self.ratings.get(user=user).rating
        except Rating.DoesNotExist:
            return None
