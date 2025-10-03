from django.utils import timezone
from django import forms
from django_recaptcha.fields import ReCaptchaField
from .models import Event
from django.contrib.gis import forms


class EventForm(forms.ModelForm):
    """
    A form for creating and updating Event instances.
    Provides fields for event details with custom widget for datetime input.
    Includes validation for required fields and date not being in the past.
    Meta:
         model (Event): The model class this form is based on
    """
    class Meta:

        model = Event
        fields = ['event_name', 'event_date', 'location', 'city', 'description', 'image']
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'city': forms.OSMWidget(attrs={"default_lat": 53.77624314030692, "default_lon": 20.47570054832161,"default_zoom": 12}),
            'image': forms.FileInput()
        }


    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.event_date:
            self.initial['event_date'] = self.instance.event_date.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()

        event_date = cleaned_data.get('event_date')
        if event_date and event_date < timezone.now():
            self.add_error('event_date', "Data wydarzenia nie może być w przeszłości")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        request = getattr(self, 'request', None)

        if request and request.user.is_authenticated:
            user = request.user
        else:
            user = None

        instance.creator = user
        instance.is_verified = request.user.is_authenticated

        if commit:
            instance.save()
        return instance
