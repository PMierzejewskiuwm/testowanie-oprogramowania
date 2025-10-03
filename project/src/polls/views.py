# polls/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import ChoiceFormSet, PollCreateForm
from .models import Choice, Poll, Vote


class PollListView(ListView):
    """
    View reponsible for listing all views.
    Uses filtering based on URL kwargs.
    """
    model = Poll
    context_object_name = 'polls'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if self.kwargs.get('filter') == 'all_non_archived':
            queryset = queryset.filter(archive_date__isnull=True)
        elif self.kwargs.get('filter') == 'all_archived':
            queryset = queryset.filter(archive_date__isnull=False)
        elif self.kwargs.get('filter') == 'my':
            if not user.is_authenticated:
                return self.handle_no_permission()
            queryset = queryset.filter(creator=user)

        queryset = queryset.prefetch_related('choices')

        annotations = {
            'choice_count': Count('choices'),
        }

        if user.is_authenticated:
            annotations['user_has_voted'] = Exists(
                Vote.objects.filter(poll=OuterRef('pk'), user=user)
            )

        return queryset.annotate(**annotations)

    def get_context_data(self, **kwargs):
        """Context used for checking filter"""
        context = super().get_context_data(**kwargs)
        context["page_param"] = 'page'
        headers = {
            'all_non_archived': "Dostępne ankiety",
            'all_archived': "Zaarchiwizowane ankiety",
            'my': "Moje ankiety",
        }
        filter_option = self.kwargs.get('filter')
        context['header_text'] = headers.get(filter_option, "Ankiety")
        return context

class PollDetailView(DetailView):
    """
    View repsponsible for displaying poll details
    as well as allow voting.
    """
    model = Poll
    context_object_name = 'poll'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = self.object
        user = self.request.user

        context['has_voted'] = False

        if user.is_authenticated:
            context['has_voted'] = Vote.objects.filter(
                poll=poll, user=user
            ).exists()

        return context

    def post(self, request, *args, **kwargs):
        poll = self.get_object()
        user = request.user

        if not user.is_authenticated:
            messages.warning(request, 'Musisz być zalogowany, aby głosować')
            return redirect('polls:poll_list')

        if Vote.objects.filter(poll=poll, user=user).exists():
            messages.error(request, 'Już zagłosowałeś w tej ankiecie!')
            return redirect('polls:poll_detail', pk=poll.pk)

        if poll.archive_date:
            messages.error(request, 'Ankieta jest już zamknięta')
            return redirect('polls:poll_detail', pk=poll.pk)

        try:
            choice = poll.choices.get(pk=request.POST.get('choice'))
        except (Choice.DoesNotExist, ValueError):
            messages.error(request, 'Nieprawidłowy wybór')
            return redirect('polls:poll_detail', pk=poll.pk)

        Vote.objects.create(poll=poll, choice=choice, user=user)
        messages.success(request, 'Twój głos został zapisany!')
        return redirect('polls:poll_results', pk=poll.pk)


class PollResultsView(DetailView):
    """
    View responsible for displaying poll results with
    vote counts and percentages.
    """
    model = Poll
    template_name = 'polls/poll_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = self.object

        choices = poll.choices.annotate(votes_count=Count('choice_votes'))
        total = poll.total_votes()

        for choice in choices:
            if total:
                choice.percentage = round((choice.votes_count / total) * 100, 1)
            else:
                choice.percentage = 0

        context.update(
            {
                'poll': poll,
                'choices': choices,
                'total_votes': total,
            }
        )
        return context


class PollCreateView(LoginRequiredMixin, CreateView):
    """
    View responsible for creating a new poll with associated choices.
    Only acessible for authenticated users.
    """
    model = Poll
    form_class = PollCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choices'] = ChoiceFormSet(
            self.request.POST if self.request.POST else None
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choices = context['choices']
        form.instance.creator = self.request.user
        message = 'Ankieta została utworzona pomyślnie.'

        if choices.is_valid():
            self.object = form.save()
            choices.instance = self.object
            choices.save()
            messages.success(self.request, message)
            return super().form_valid(form)

        return self.form_invalid(form)

    def handle_no_permission(self):
        messages.error(
            self.request, 'Musisz być zalogowany, aby dodać ankietę.'
        )
        return redirect('users:register')

    def get_success_url(self):
        return reverse_lazy('polls:list_poll')

class PollDeleteView(LoginRequiredMixin, DeleteView):
    """
    View resonsible for deleting polls by their owners.
    """
    model = Poll
    success_url = reverse_lazy('polls:list_poll')

    def delete(self, request, *args, **kwargs):
        """Add success message after deletion."""
        messages.success(request, 'Ankieta została usunięta!')
        return super().delete(request, *args, **kwargs)


class PollArchiveView(LoginRequiredMixin, View):
    """
    View reponsible for arachiving specific poll by their owners.
    """
    model = Poll

    def post(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)

        if request.user == poll.creator:
            poll.archive_poll()
        else:
            messages.error(request, 'Nie masz uprawnień do tej akcji')
        return redirect('polls:poll_detail', pk=pk)
