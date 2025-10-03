from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image

from comments_and_ratings.models import Rating
from myApp.utils.upload_pather import dynamic_image_upload_pather


class Gallery(models.Model):
    """
    A model representing an event in the system.

    Attributes:
    title (CharField): The title of the gallery (maximum 100 characters).
    description (TextField): A brief description of the gallery (maximum 500 characters).
    created_at (DateTimeField): The date and time when the gallery was created.
    updated_at (DateTimeField): The date and time when the gallery was last updated.
    creator (ForeignKey): A reference to the user who created the gallery.
    thumbnail (ImageField): An image representing the gallery thumbnail.
    slug (SlugField): A unique URL-friendly identifier for the gallery.

    """
    title = models.CharField(max_length=100, verbose_name="tytuł galerii")
    description = models.TextField(max_length=500, verbose_name="opis galerii")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="twórca galerii"
    )
    thumbnail = models.ImageField(
        upload_to=dynamic_image_upload_pather,
        verbose_name="miniaturka galerii"
    )
    slug = models.SlugField(max_length=100, unique=True)

    ratings = GenericRelation('comments_and_ratings.Rating')
    comments = GenericRelation('comments_and_ratings.Comment')

    class Meta:
        verbose_name = "Galeria"
        verbose_name_plural = "Galerie"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to automatically generate a slug and process the thumbnail image.

        If the slug is not already set, it is generated from the gallery title using Django's `slugify`.
        After saving, if a thumbnail image is provided, it is opened, converted to RGB,
        resized to a maximum of 400x300 pixels and saved as a JPEG with 85% quality.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the absolute URL to the detail view of this gallery using its slug.
        """
        return reverse('photo_gallery:gallery_detail', kwargs={'slug': self.slug})

    def get_creator_name(self):
        """
        Returns the name of the gallery creator.

        Returns:
            str: Username
        """
        return self.creator.username

    def __str__(self):
        """
        Returns the string representation of the event, which is the title.
        """
        return self.title

    @property
    def average_rating(self):
        result = self.ratings.aggregate(models.Avg('rating'))
        return round(result['rating__avg'], 1) if result['rating__avg'] else None

    def get_user_rating(self, user):
        try:
            return self.ratings.get(user=user).rating
        except Rating.DoesNotExist:
            return None


class Photo(models.Model):
    """
    A model representing a photo within a gallery.

    Attributes:
        gallery (ForeignKey): A reference to the gallery this photo belongs to.
        title (CharField): The title of the photo (maximum 100 characters).
        image (ImageField): The image file associated with the photo.
        description (TextField): An optional description of the photo (maximum 500 characters).
        uploaded_at (DateTimeField): The date and time when the photo was uploaded.
    """
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    title = models.CharField(max_length=100, verbose_name="tytuł zdjęcia")
    image = models.ImageField(upload_to=dynamic_image_upload_pather)
    description = models.TextField(max_length=500, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    ratings = GenericRelation('comments_and_ratings.Rating')
    comments = GenericRelation('comments_and_ratings.Comment')

    class Meta:
        verbose_name = "Zdjęcie"
        verbose_name_plural = "Zdjęcia"
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to process the uploaded image.

        After saving the instance, the image is opened, converted to RGB,
        resized to a maximum size of 400x300 pixels,
        and saved in JPEG format with 85% quality to reduce file size.
        """
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns the string representation of the photo, which is the title.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the absolute URL to the detail view of the photo.

        The URL includes the slug of the associated gallery and the primary key of the photo.
        """
        return reverse('photo_gallery:photo_detail', kwargs={'slug': self.gallery.slug, 'pk': self.pk})

    @property
    def average_rating(self):
        result = self.ratings.aggregate(models.Avg('rating'))
        return round(result['rating__avg'], 1) if result['rating__avg'] else None

    def get_user_rating(self, user):
        try:
            return self.ratings.get(user=user).rating
        except Rating.DoesNotExist:
            return None
