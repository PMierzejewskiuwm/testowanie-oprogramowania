from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, FileExtensionValidator
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from .models import UserProfile
from datetime import date


class ProfileUpdateForm(forms.ModelForm):
    """
    A form for updating a user's profile information, including description,
    birth date, profile picture, and phone number.
    Validation is included, such as checking phone number format and allowed file
    extensions for profile pictures.
    """
    class Meta:
        model = UserProfile
        fields = ['description', 'birth_date', 'profile_picture', 'phone_number']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Opisz siebie w kilku zdaniach...'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'max': str(date.today())
            },  format='%Y-%m-%d'),

            'phone_number': forms.TextInput(attrs={
                'placeholder': '+48 123 456 789'
            })
        }
        labels = {
            'description': 'Opis profilu',
            'birth_date': 'Data urodzenia',
            'profile_picture': 'Zdjęcie profilowe',
            'phone_number': 'Numer telefonu'
        }

        validators = {
            'profile_picture': [
                FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            ]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].input_formats = ['%Y-%m-%d']
        self.fields['phone_number'].validators.append(
            RegexValidator(
                regex=r'^\d{9}$',
                message="Numer telefonu musi składać się z dokładnie 9 cyfr (bez spacji, myślników i znaków specjalnych)"
            )
        )

class EmailChangeForm(forms.Form):
    """
    A form for changing the user's email address, requiring the user to confirm
    their current password.
    Validates that the provided password matches the user's current password
    before allowing the email change to proceed.
    """
    new_email = forms.EmailField(label="Nowy email")
    current_password = forms.CharField(
        label="Obecne hasło",
        widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')

        if current_password and not self.user.check_password(current_password):
            raise forms.ValidationError("Nieprawidłowe obecne hasło")

        return cleaned_data


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    """
    A custom password change form with modified field labels, input attributes,
    and additional help text.
    """

    old_password = forms.CharField(
        label="Obecne hasło",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )
    new_password1 = forms.CharField(
        label="Nowe hasło",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Hasło powinno mieć minimum 8 znaków, zawierać cyfry i litery."
    )
    new_password2 = forms.CharField(
        label="Powtórz nowe hasło",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

class UsernameChangeForm(forms.Form):
    """
    A form for changing the user's username, requiring the current password
    for verification.
    Validates both the provided password and ensures that the new username
    is not already taken by another user.
    """
    new_username = forms.CharField(label="Nowa nazwa użytkownika", max_length=30)
    current_password = forms.CharField(
        label="Obecne hasło",
        widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('current_password')
        if password and not self.user.check_password(password):
            raise forms.ValidationError("Nieprawidłowe obecne hasło.")
        return cleaned_data

    def clean_new_username(self):
        username = self.cleaned_data.get('new_username')
        from django.contrib.auth import get_user_model
        user = get_user_model()
        if user.objects.filter(username=username).exists():
            raise forms.ValidationError("Taka nazwa użytkownika już istnieje.")
        return username
