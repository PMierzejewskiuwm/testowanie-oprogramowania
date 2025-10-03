from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from myApp.utils.upload_pather import dynamic_image_upload_pather


class UserProfile(models.Model):
    """
    A model representing additional profile information for a user.

    Attributes:
        user (OneToOneField): The associated user account (linked to the AUTH_USER_MODEL).
        description (TextField): Optional short biography or profile description (max 500 characters).
        birth_date (DateField): Optional user's date of birth.
        profile_picture (ImageField): Optional profile image uploaded by the user.
        phone_number (CharField): Optional contact phone number (max 20 characters).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    description = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to=dynamic_image_upload_pather, blank=True, null=True)
    phone_number = models.CharField(max_length=9, blank=True)

    def __str__(self):
        """
        Returns the string representation of the user profile, which is the username of the user.
        """
        return f'Profile of {self.user.username}'

