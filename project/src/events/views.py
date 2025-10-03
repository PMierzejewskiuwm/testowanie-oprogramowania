from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin

from comments_and_ratings.forms import CommentForm
from .models import Event
from .forms import EventForm
from django.db.models import Q, Case, When, IntegerField


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_verified=True)

        match self.kwargs.get('filter'):
            case 'all_non_archived':
                queryset = queryset.filter(is_archived=False)
            case 'all_archived':
                queryset = queryset.filter(is_archived=True)
            case 'my':
                if not self.request.user.is_authenticated:
                    return self.handle_no_permission()
                queryset = queryset.filter(creator=self.request.user)

        if search_for := self.request.GET.get('keyword'):
            queryset = queryset.filter(
                Q(event_name__icontains=search_for) |
                Q(description__icontains=search_for) |
                Q(location__icontains=search_for)
            )

        if filter_location := self.request.GET.get('location'):
            queryset = queryset.filter(location=filter_location)

        sort_by = self.request.GET.get('sort_by')
        sort_options = {
            'event_date': 'event_date',
            '-event_date': '-event_date',
            'created_at': 'created_at',
            '-created_at': '-created_at',
            'updated_at': 'updated_at',
            '-updated_at': '-updated_at'
        }

        if self.kwargs['filter'] == 'my':
            queryset = queryset.annotate(
                is_archived_flag=Case(
                    When(is_archived=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )

        if sort_by in sort_options:
            if self.kwargs['filter'] == 'my':
                queryset = queryset.order_by(
                    'is_archived_flag',
                    sort_options[sort_by]
                )
            else:
                queryset = queryset.order_by(
                    sort_options[sort_by]
                )
        else:
            if self.kwargs['filter'] == 'my':
                queryset = queryset.order_by(
                    'is_archived_flag',
                    '-event_date'
                )
            else:
                queryset = queryset.order_by(
                    '-event_date'
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_filter = self.kwargs.get('filter')

        context.update({
            'is_all_events': current_filter == 'all_non_archived',
            'is_archived': current_filter == 'all_archived',
            'is_my_events': current_filter == 'my',
            'request': self.request,
            'page_param': "page",
            'selected_location': self.request.GET.get('location', ''),
            'current_filter': current_filter
        })

        sort_by = self.request.GET.get('sort_by', '-event_date')
        context['sort_options'] = [
            {
                'value': '-event_date',
                'label': 'Data wydarzenia: od najnowszej',
                'selected': sort_by == '-event_date'
            },
            {
                'value': 'event_date',
                'label': 'Data wydarzenia: od najstarszej',
                'selected': sort_by == 'event_date'
            },
            {
                'value': '-created_at',
                'label': 'Data dodania: od najnowszej',
                'selected': sort_by == '-created_at'
            },
            {
                'value': 'created_at',
                'label': 'Data dodania: od najstarszej',
                'selected': sort_by == 'created_at'
            },
            {
                'value': '-updated_at',
                'label': 'Data modyfikacji: od najnowszej',
                'selected': sort_by == '-updated_at'
            },
            {
                'value': 'updated_at',
                'label': 'Data modyfikacji: od najstarszej',
                'selected': sort_by == 'updated_at'
            }
        ]

        if context['is_my_events']:
            context['available_locations'] = (Event.objects
                                           .filter(creator=self.request.user)
                                           .order_by('location')
                                           .values_list('location', flat=True)
                                           .distinct())
        else:
            context['available_locations'] = (Event.objects
                                           .order_by('location')
                                           .values_list('location', flat=True)
                                           .distinct())

        return context



class EventDetailView(DetailView):
    """View showing event details: """
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        content_type = ContentType.objects.get_for_model(event)
        object_id = event.id

        context['content_type'] = content_type
        context['object_id'] = object_id
        context['comments'] = event.comments.filter(parent_comment__isnull=True).order_by('-created_at')
        context['comment_form'] = CommentForm()
        context['average_rating'] = event.average_rating
        context['ratings_count'] = event.ratings.count()

        if self.request.user.is_authenticated:
            rating_obj = event.ratings.filter(user=self.request.user).first()
            context['user_rating'] = rating_obj.rating if rating_obj else None
            context['user_rating_id'] = rating_obj.id if rating_obj else None

        if event.average_rating is not None:
            average = float(context['average_rating'])
            full_stars = int(average)
            has_half = (average - full_stars) >= 0.5
            empty_stars = 10 - full_stars - (1 if has_half else 0)

            context.update({
                'stars_data': {
                    'full': full_stars,
                    'half': has_half,
                    'empty': empty_stars
                }
            })
        else:
            context.update({
                'stars_data': {
                    'full': 0,
                    'half': False,
                    'empty': 10
                }
            })

        return context


class EventCreateView(CreateView):
    """
    View allowing to create new event.
    Uses Django's generic CreateView.
    """
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('events:list_event')

    def get_form_kwargs(self):
        """Pass the request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Add success messages for valid form."""
        message = 'Dziękujemy za dodanie wydarzenia. Zostanie ono opublikowane po weryfikacji przez administratora.'
        if self.request.user.is_authenticated:
            message = 'Wydarzenie zostało dodane.'
        messages.success(self.request, message)
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    """
    View managing editing of an existing event.
    Uses Django's generic UpdateView.
    """
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('events:user_event_list')

    def get_form_kwargs(self):
        """Pass the request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Add success messages for valid form."""
        messages.success(self.request, f"{self.model._meta.verbose_name} zostało zaktualizowane!")
        return super().form_valid(form)

class EventDeleteView(LoginRequiredMixin, DeleteView):
    """
    View managing deletion of an existing event.
    Uses Django's generic DeleteView.
    """
    model = Event
    success_url = reverse_lazy('events:user_event_list')

    def form_valid(self, form):
        """Add success message after deletion."""
        messages.success(self.request,f"{self.model._meta.verbose_name}  zostało usunięte!")
        return super().form_valid(form)