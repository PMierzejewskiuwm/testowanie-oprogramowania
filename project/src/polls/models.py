from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


# Create your models here.
class Poll(models.Model):
    """Class representing a poll in the system.

    Args:
        question(TextField): Question of the poll.
        creation_date(DateTimeField): Date at which poll was created.
        end_date(DateTimeField): Date at which poll ends.
        archive_data(DateTimeField): Date at which poll was archived.
        creator(ForeignKey): Creator of the poll (associated with the user
        model).
    """
    question = models.TextField(verbose_name='pytanie ankiety')
    creation_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='data utworzenia'
    )
    end_date = models.DateTimeField(verbose_name='data zamknięcia')
    archive_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='data archiwizacji'
    )
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='twórca ankiety',
    )

    def __str__(self):
        return self.question

    def total_votes(self):
        """
        Method counting all votes within a poll, uses
        relation name which is poll_votes.
        """
        return self.poll_votes.count()

    def archive_poll(self):
        """
        Sets the poll status to archived.
        Updates 'archive_date' only.
        """
        self.archive_date = timezone.now()
        self.save(update_fields=['archive_date'])

    class Meta:
        verbose_name = 'ankieta'
        verbose_name_plural = 'ankiety'


class Choice(models.Model):
    """Class representing a choice in the poll.

    Args:
    text(CharField): Text of the choice (max_len=200)
    poll(ForeignKey): Poll to which this choice is bound to
    """
    text = models.CharField(max_length=200, verbose_name='reprezentacja opcji')
    poll = models.ForeignKey(
        Poll,
        related_name='choices',
        on_delete=models.CASCADE,
        verbose_name='ankieta',
    )

    def __str__(self):
        return self.text

    def vote_count(self):
        """
        Method counting votes for a choice,
        uses relation name which is poll_votes.
        """
        return self.choice_votes.count()

    class Meta:
        verbose_name = 'wybór'
        verbose_name_plural = 'wybory'


class Vote(models.Model):
    """Class representing a vote for a choice in a poll.

    Args:
        creator(ForeignKey): User who voted (associated with the user
        model).
        poll(ForeignKey): Poll in which vote was given.
        choice(ForeignKey): Choice which was voted for.
        vote_date(DateTimeField): Date at which the vote was given.
    """
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, verbose_name='głosujący'
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='poll_votes',
        verbose_name='ankieta'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='choice_votes',
        verbose_name='decyzja'
    )
    vote_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='data zagłosowania'
    )

    class Meta:
        indexes = [
            models.Index(fields=['poll']),
            models.Index(fields=['choice']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['poll', 'user'], name='unique_user_vote'
            )
        ]
        verbose_name = 'głos'
        verbose_name_plural = 'głosy'

    def __str__(self):
        return f'{self.user} zagłosował na {self.choice}'
