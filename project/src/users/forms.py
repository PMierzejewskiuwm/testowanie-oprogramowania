from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django_recaptcha.fields import ReCaptchaField

from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """
    A form for creating CustomUser instances.
    - Requires a valid and unique email address.
    - Validates that the username does not exceed 30 characters.
    - Adds custom error messages for email, username, and passwords.
    - Ensures that both entered passwords match.
    Meta:
        model (CustomUser): The model class this form is based on
    """
    email = forms.EmailField(
        required=True,
        label="Email",
        error_messages={
            'invalid': 'Wprowadź poprawny adres email.',
            'required': 'Email jest wymagany.'
        }
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        error_messages = {
            'username': {
                'required': 'Nazwa użytkownika jest wymagana.',
                'unique': 'Użytkownik o tej nazwie już istnieje.'
            },
        }

    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].error_messages = {
            'required': 'Hasło jest wymagane.',
            'password_too_short': 'Hasło jest zbyt krótkie.',
            'password_too_common': 'Hasło jest zbyt powszechne.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Potwierdzenie hasła jest wymagane.',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) > 30:
            raise forms.ValidationError('Login może mieć maksymalnie 30 znaków.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Ten adres email jest już zarejestrowany.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Podane hasła nie są identyczne.")

        return cleaned_data


class LoginForm(forms.Form):
    """Login form for authentication by email and password."""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user_obj = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Niepoprawny e-mail lub hasło.")

            user = authenticate(username=user_obj.username, password=password)
            if user is None:
                raise forms.ValidationError("Niepoprawny e-mail lub hasło.")

            self.user = user
        return cleaned_data