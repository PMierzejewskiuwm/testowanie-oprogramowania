from django import forms
from django_recaptcha.fields import ReCaptchaField

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    """
    A form for creating and updating Announcement instances.
    Provides fields for announcement details with custom widget for datetime
    input.

    Meta:
         model (Announcement): The model class this form is based on
         fields (list): The fields to include in the form -
                        ['title',
                        'place',
                        'rooms',
                        'price',
                        'description',
                        'banner']
         widgets (dict): Custom widgets for form fields, including:
                        - DateTimeInput with datetime-local type for event_date

    captcha - captcha provided by google API keys
    """

    class Meta:
        model = Announcement
        fields = ['title',
                  'place',
                  'rooms',
                  'price',
                  'description',
                  'banner']

        widgets = {
          'banner': forms.FileInput()
        }

    captcha = ReCaptchaField()
