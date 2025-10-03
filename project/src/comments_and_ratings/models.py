from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Rating(models.Model):
    """
    A model representing a user rating associated with any content type.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="zawartosc do oceny"
    )
    object_id = models.PositiveIntegerField(verbose_name="id oceny")
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="oceniajacy uzytkownik"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="ocena"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="data utworzenia oceny"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="data edycji oceny"
    )

    class Meta:
        verbose_name = "Ocena"
        verbose_name_plural = "Oceny"
        unique_together = ('content_type', 'object_id', 'user')

    def __str__(self):
        return f"{self.rating}/10 by {self.user.username} for {self.content_object}"


class Comment(models.Model):
    """
    A model representing a user comment with optional nested replies.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="zawartosc do komentowania"
    )
    object_id = models.PositiveIntegerField(verbose_name="id komentarza")
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="oceniajacy uzytkownik"
    )
    parent_comment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    content = models.TextField(
        max_length=500,
        verbose_name="treść komentarza"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="data utworzenia komentarza"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="data edycji komentarza"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="czy aktywny"
    )

    class Meta:
        verbose_name = "Komentarz"
        verbose_name_plural = "Komentarze"
        ordering = ['-created_at']

    def __str__(self):
        return f"Komentarz {self.id} przez {self.user.username}"

    def get_replies(self):
        """Returns all active replies to this comment."""
        return self.replies.filter(is_active=True)

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent_comment is not None
