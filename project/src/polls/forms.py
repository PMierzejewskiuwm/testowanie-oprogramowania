from django import forms
from django.utils.timezone import localtime, now
from django_recaptcha.fields import ReCaptchaField

from .models import Choice, Poll


class PollCreateForm(forms.ModelForm):
    """
    Form for poll creation. Validates if date is not
    in the past.
    """
    class Meta:
        model = Poll
        fields = ['question', 'end_date']
        widgets = {
            'question': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Podaj pytanie'
            }),
            'end_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'min': localtime(now()).now().strftime('%Y-%m-%dT%H:%M')
                }
            ),
        }

    captcha = ReCaptchaField()

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['end_date'].widget.attrs['min'] = localtime(now()).strftime(
            '%Y-%m-%dT%H:%M'
        )

    def clean(self):
        cleaned_data = super().clean()

        end_date = cleaned_data.get('end_date')
        if end_date <= localtime(now()):
            raise forms.ValidationError('Wybierz prawidłową datę.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.creator = self.user
        if commit:
            instance.save()
        return instance


class ChoiceForm(forms.ModelForm):
    """Form for a specific choice."""
    class Meta:
        model = Choice
        fields = ['text']
        widgets = {
            'text': forms.TextInput(
                attrs={'placeholder': 'Wstaw treść odpowiedzi...'})
        }


ChoiceFormSet = forms.inlineformset_factory(
    parent_model=Poll,
    model=Choice,
    form=ChoiceForm,
    extra=0,
    min_num=2,
    validate_min=True,
    max_num=8,
    validate_max=True,
)
