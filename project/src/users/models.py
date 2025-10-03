from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    This model overrides the default user model by ensuring that
    email is unique and the max length of username is 30.
    """

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)

    def __str__(self):
        """
        Returns the string representation of the user, which is the username.
        """
        return self.username