from django.utils import timezone
from django import forms
from django.forms import ModelForm
from django_recaptcha.fields import ReCaptchaField

class ContactForm(forms.Form):
    """
    A form for sending e-mails.
    Provides fields for e-mail details.
    Includes validation for required fields.

    email - input field for emails from which the message is sent
    subject - input field for email's subject
    message - input field for email's content

    captcha - captcha provided by google API keys
    """
    email = forms.EmailField(label="e-mail")
    subject = forms.CharField(label="Temat",max_length=100)
    message = forms.CharField(label="Wiadomość", widget=forms.Textarea)
    captcha = ReCaptchaField(label='')
