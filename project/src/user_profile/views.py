from django.views.generic import DetailView, UpdateView, TemplateView, FormView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import UserProfile
from .forms import ProfileUpdateForm, EmailChangeForm, CustomPasswordChangeForm, UsernameChangeForm


class UserProfileView(LoginRequiredMixin, DetailView):
    """
    View displaying the logged-in user's profile details.

    - Requires authentication.
    - Retrieves the UserProfile instance related to the current user.
    """
    model = UserProfile
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """
        Returns the UserProfile associated with the currently logged-in user.
        Creates a new profile if profile does not exist.
        """
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=self.request.user)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View allowing the logged-in user to edit their profile.

    - Uses ProfileUpdateForm to edit profile fields.
    - Displays a success message upon successful update.
    """
    model = UserProfile
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('user_profile:profile')

    def form_valid(self, form):
        """Add success messages for valid form."""
        messages.success(self.request, 'Profil został zaktualizowany!')
        return super().form_valid(form)

    def get_object(self, queryset=None):
        """
        Returns the UserProfile associated with the currently logged-in user.
        Creates a new profile if profile does not exist.
        """
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=self.request.user)


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """
    View displaying user account settings.

    - Provides forms for changing password and email.
    - Injects both forms into the context for rendering in the template.
    """
    template_name = 'user_profile/account_settings.html'


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View allowing the user to change their password.

    - Uses CustomPasswordChangeForm.
    - Displays success or error messages depending on the outcome.
    """
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('user_profile:account_settings')
    template_name = 'user_profile/password_change.html'

    def form_valid(self, form):
        """Add success message for valid form."""
        messages.success(self.request, 'Hasło zostało zmienione!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Add error message for valid form."""
        messages.error(self.request, 'Wystąpił błąd podczas zmiany hasła.')
        return super().form_invalid(form)


class UserEmailChangeView(LoginRequiredMixin, FormView):
    """
    View allowing the user to change their email address.

    - Validates the user's current password.
    - Saves the new email to the user model.
    - Displays success or error messages depending on the outcome.
    """
    form_class = EmailChangeForm
    success_url = reverse_lazy('user_profile:account_settings')
    template_name = 'user_profile/email_change.html'

    def get_form_kwargs(self):
        """Pass the request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Add success messages for valid form."""
        self.request.user.email = form.cleaned_data['new_email']
        self.request.user.save()
        messages.success(self.request, 'Email został zmieniony!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Add error message for valid form."""
        messages.error(self.request, 'Wystąpił błąd podczas zmiany emaila.')
        return super().form_invalid(form)

class UsernameChangeView(LoginRequiredMixin, FormView):
    """
    View allowing the user to change their username.

    - Validates current password.
    - Ensures the new username is unique.
    - Saves the new username and shows a success message.
    """
    template_name = 'user_profile/username_change.html'
    form_class = UsernameChangeForm
    success_url = reverse_lazy('user_profile:account_settings')

    def get_form_kwargs(self):
        """Pass the request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Add success messages for valid form."""
        self.request.user.username = form.cleaned_data['new_username']
        self.request.user.save()
        messages.success(self.request, "Nazwa użytkownika została zmieniona.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Add error message for valid form."""
        messages.error(self.request, "Wystąpił błąd podczas zmiany nazwy użytkownika.")
        return super().form_invalid(form)
