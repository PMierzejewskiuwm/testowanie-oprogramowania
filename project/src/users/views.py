from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LogoutView
from django.contrib.auth import login, authenticate
from .models import CustomUser
from .forms import RegistrationForm, LoginForm


class RegisterView(CreateView):
    """View handling user registration.
    - Uses the custom RegistrationForm for user creation.
    - Displays success message on successful registration.
    - Displays field-specific error messages on failure.
    """

    model = CustomUser
    form_class = RegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:register')

    def form_valid(self, form):
        """Add success messages for valid form."""
        messages.success(self.request, "Rejestracja przebiegła pomyślnie!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return super().form_invalid(form)


class LoginView(FormView):
    """View handling user login via email and password."""
    form_class = LoginForm
    template_name = 'layout.html'
    success_url = reverse_lazy('user_profile:profile')

    def form_valid(self, form):
        login(self.request, form.user)
        messages.success(self.request, f"Witaj {form.user.username}! Zostałeś zalogowany.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return redirect('/')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_login_modal'] = True
        return context


class CustomLogoutView(LogoutView):
    """
    View handling user logout.
    - Logs out the user and redirects to the homepage.
    """
    next_page = reverse_lazy('homepage')