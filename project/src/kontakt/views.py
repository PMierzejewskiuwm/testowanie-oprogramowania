from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.forms import forms
from django.contrib import messages
from .forms import ContactForm
from django.views.generic import FormView

# Create your views here.
class ContactView(FormView):
    """View handling sending mail via form"""
    form_class = ContactForm
    template_name = 'kontakt/formularz_kontaktowy.html'
    success_url = reverse_lazy('formularz')
    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")

        try:
            send_mail(subject, message, email, [settings.EMAIL_HOST_USER])
        except BadHeaderError:
            messages.error(self.request, "Wykryto niepoprawny nagłówek.")
        else:
            messages.success(self.request, "Pomyślnie wysłano mail.")

        return super(ContactView, self).form_valid(form)