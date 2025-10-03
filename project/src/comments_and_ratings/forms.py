from django import forms
from django_recaptcha.fields import ReCaptchaField
from .models import Rating, Comment


class RatingForm(forms.ModelForm):
    """
    A form for submitting a numeric rating (1–10) for any content object.

    Meta:
        model (Rating): The model class this form is based on.
        fields (list): Contains only the 'rating' field.
        widgets (dict): Custom number input with min/max and CSS class.
    """
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'rating-input'})
        }


class CommentForm(forms.ModelForm):
    """
    A form for submitting a top-level comment for any content object.

    Meta:
        model (Comment): The model class this form is based on.
        fields (list): Contains only the 'content' field.
        widgets (dict): Textarea widget with placeholder and styling.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Dodaj komentarz...',
                'class': 'comment-textarea'
            })
        }

    captcha = ReCaptchaField()


class ReplyForm(forms.ModelForm):
    """
    A form for submitting a reply to an existing comment.

    Meta:
        model (Comment): The model class this form is based on.
        fields (list): Contains only the 'content' field.
        widgets (dict): Textarea widget with reply-specific placeholder and styling.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Odpowiedz na komentarz...',
                'class': 'reply-textarea'
            })
        }
