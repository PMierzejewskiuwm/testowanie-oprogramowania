from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DeleteView, UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from .models import Rating, Comment
from .forms import RatingForm, CommentForm, ReplyForm


class AddRatingView(LoginRequiredMixin, CreateView):
    """View allowing logged-in users to add or update a rating for an object."""
    model = Rating
    form_class = RatingForm

    def dispatch(self, request, *args, **kwargs):
        """Get content type and object ID from URL kwargs."""
        self.content_type = get_object_or_404(
            ContentType,
            app_label=kwargs['app_label'],
            model=kwargs['model_name']
        )
        self.object_id = kwargs['object_id']
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Create or update the rating, then redirect with a message."""
        rating, created = Rating.objects.update_or_create(
            content_type=self.content_type,
            object_id=self.object_id,
            user=self.request.user,
            defaults={'rating': form.cleaned_data['rating']},
        )

        if created:
            messages.success(self.request, "Dziękujemy za ocenę!")
        else:
            messages.success(self.request, "Twoja ocena została zaktualizowana!")

        return redirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to the referring page."""
        return self.request.META.get('HTTP_REFERER', '/')


class AddCommentView(LoginRequiredMixin, CreateView):
    """View allowing logged-in users to add a comment to an object."""
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        """Get content type and object ID from URL kwargs."""
        self.content_type = get_object_or_404(
            ContentType,
            app_label=kwargs['app_label'],
            model=kwargs['model_name']
        )
        self.object_id = kwargs['object_id']
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Save comment with content object and user info, then redirect."""
        comment = form.save(commit=False)
        comment.content_type = self.content_type
        comment.object_id = self.object_id
        comment.user = self.request.user
        comment.save()

        messages.success(self.request, "Twój komentarz został dodany!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """Handle invalid form submission."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Błąd w polu {field}: {error}")

        return redirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to the referring page."""
        return self.request.META.get('HTTP_REFERER', '/')


class AddReplyView(LoginRequiredMixin, CreateView):
    """View allowing logged-in users to reply to a specific comment."""
    model = Comment
    form_class = ReplyForm

    def dispatch(self, request, *args, **kwargs):
        """Retrieve the parent comment from the URL."""
        self.parent_comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Save reply with parent comment and user info, then redirect."""
        reply = form.save(commit=False)
        reply.content_type = self.parent_comment.content_type
        reply.object_id = self.parent_comment.object_id
        reply.user = self.request.user
        reply.parent_comment = self.parent_comment
        reply.save()

        messages.success(self.request, "Twoja odpowiedź została dodana!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to the referring page."""
        return self.request.META.get('HTTP_REFERER', '/')


class EditCommentView(LoginRequiredMixin, UpdateView):
    """View allowing users to edit their own comment."""
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        """Display success message and redirect to the related object."""
        self.content_object = self.object.content_object
        messages.success(self.request, "Komentarz został zaktualizowany!")
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the related object's detail page."""
        return self.content_object.get_absolute_url()


class DeleteRatingOrCommentView(LoginRequiredMixin, DeleteView):
    """Allow users to delete their own rating or comment."""
    model = Rating
    template_name = 'comments_and_ratings/confirm_delete.html'
    success_message = ''
    is_comment = True

    def form_valid(self, form):
        self.content_object = self.object.content_object
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return self.content_object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_comment'] = self.is_comment
        return context
