from django import forms
from django_recaptcha.fields import ReCaptchaField

from .models import Gallery, Photo

class GalleryForm(forms.ModelForm):
    """
    A form for creating and updating Gallery instances.
    Meta:
        model (Gallery): The model class this form is based on

    captcha - captcha provided by google API keys
    """
    class Meta:
        model = Gallery
        fields = ['title', 'description', 'thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Gallery.objects.filter(title=title).exists():
            raise forms.ValidationError("Galeria o tej nazwie już istnieje.")
        return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.creator = self.user
        if commit:
            instance.save()
        return instance


class PhotoForm(forms.ModelForm):
    """
    A form for creating and updating Gallery instances.
    Meta:
        model (Gallery): The model class this form is based on

    captcha - captcha provided by google API keys
    """
    class Meta:
        model = Photo
        fields = ['title', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        self.gallery = kwargs.pop('gallery', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.gallery = self.gallery
        if commit:
            instance.save()
        return instance