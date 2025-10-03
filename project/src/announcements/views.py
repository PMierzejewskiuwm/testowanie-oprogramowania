from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, Case, When, IntegerField
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from comments_and_ratings.forms import CommentForm
from .forms import AnnouncementForm
from .models import Announcement


class AnnouncementListView(ListView):
    model = Announcement
    context_object_name = 'announcements'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_verified=True)

        if self.kwargs.get('filter') == 'all_non_archived':
            queryset = queryset.filter(archive_date__isnull=True)
        elif self.kwargs.get('filter') == 'all_archived':
            queryset = queryset.filter(archive_date__isnull=False)
        elif self.kwargs.get('filter') == 'my':
            if not self.request.user.is_authenticated:
                return self.handle_no_permission()
            queryset = queryset.filter(creator=self.request.user)

        if search_for := self.request.GET.get('keyword'):
            queryset = queryset.filter(
                Q(title__icontains=search_for) |
                Q(description__icontains=search_for) |
                Q(place__icontains=search_for)
            )

        if filter_place := self.request.GET.get('place'):
            queryset = queryset.filter(place=filter_place)

        sort_by = self.request.GET.get('sort_by')
        sort_options = {
            'date': 'date',
            '-date': '-date',
            'price': 'price',
            '-price': '-price',
            'rooms': 'rooms',
            '-rooms': '-rooms'
        }


        if self.kwargs['filter'] == 'my':
            queryset = queryset.annotate(
                is_archived_flag=Case(
                    When(archive_date__isnull=False, then=1),
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
                    '-date'
                )
            else:
                queryset = queryset.order_by(
                    '-date'
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_filter = self.kwargs.get('filter')

        context.update({
            'is_all_announcements': current_filter in ['all_non_archived', 'all_archived'],
            'is_archived': current_filter == 'all_archived',
            'is_my_announcements': current_filter == 'my',
            'request': self.request,
            'page_param': "page",
            'selected_place': self.request.GET.get('place', ''),
            'current_filter': current_filter
        })

        sort_by = self.request.GET.get('sort_by', '-date')
        context['sort_options'] = [
            {
                'value': '-date',
                'label': 'Data dodania: od najnowszej',
                'selected': sort_by == '-date'
            },
            {
                'value': 'date',
                'label': 'Data dodania: od najstarszej',
                'selected': sort_by == 'date'
            },
            {
                'value': 'price',
                'label': 'Cena: od najniższej',
                'selected': sort_by == 'price'
            },
            {
                'value': '-price',
                'label': 'Cena: od najwyższej',
                'selected': sort_by == '-price'
            },
            {
                'value': 'rooms',
                'label': 'Ilość pokoi: od najmniejszej',
                'selected': sort_by == 'rooms'
            },
            {
                'value': '-rooms',
                'label': 'Ilość pokoi: od największej',
                'selected': sort_by == '-rooms'
            }
        ]

        if context['is_my_announcements']:
            context['available_places'] = (Announcement.objects
                                           .filter(creator=self.request.user)
                                           .order_by('place')
                                           .values_list('place', flat=True)
                                           .distinct())
        else:
            context['available_places'] = (Announcement.objects
                                           .order_by('place')
                                           .values_list('place', flat=True)
                                           .distinct())

        return context


class AnnouncementDetailView(DetailView):
    """View showing announcement details:"""

    model = Announcement
    context_object_name = 'announcement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        announcement = self.object

        content_type = ContentType.objects.get_for_model(announcement)
        object_id = announcement.id

        context['content_type'] = content_type
        context['object_id'] = object_id
        context['comments'] = announcement.comments.filter(parent_comment__isnull=True).order_by('-created_at')
        context['comment_form'] = CommentForm()
        context['average_rating'] = announcement.average_rating
        context['ratings_count'] = announcement.ratings.count()

        if self.request.user.is_authenticated:
            rating_obj = announcement.ratings.filter(user=self.request.user).first()
            context['user_rating'] = rating_obj.rating if rating_obj else None
            context['user_rating_id'] = rating_obj.id if rating_obj else None

        if announcement.average_rating is not None:
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


class AnnouncementCreateView(CreateView):
    """
    View responsible for creating an announcement.
    Uses Django's generic CreateView.
    """

    model = Announcement
    form_class = AnnouncementForm

    def form_valid(self, form):
        form.instance.creator = None
        custom_message = ('Ogłoszenie czeka na weryfikacje'
                          'ze strony administracji.')

        if self.request.user.is_authenticated:
            form.instance.creator = self.request.user
            form.instance.is_verified = True
            custom_message = 'Ogłoszenie zostało pomyślnie dodane.'

        messages.success(self.request, custom_message)
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse_lazy('announcements:user_announcement_list')
        return reverse_lazy('announcements:list_announcement')


class AnnouncementUpdateView(LoginRequiredMixin, UpdateView):
    """
    View responsible for updating user specific announcement.
    Uses Django's generic UpdateView.
    """

    model = Announcement
    success_url = reverse_lazy('announcements:user_announcement_list')
    form_class = AnnouncementForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        return form


class AnnouncementDeleteView(LoginRequiredMixin, DeleteView):
    """
    View responsible for removing user specific announcement.
    Uses Django's generic DeleteView.
    """

    model = Announcement
    success_url = reverse_lazy('announcements:user_announcement_list')

    def delete(self, request, *args, **kwargs):
        """Add success message after deletion."""
        messages.success(request, 'Ogłoszenie zostało usunięte!')
        return super().delete(request, *args, **kwargs)


class AnnouncementToggleArchiveView(LoginRequiredMixin, View):
    """
    View reponsible for toggling archive status of the announcement.
    """
    model = Announcement

    def post(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)

        if request.user == announcement.creator:
            if announcement.archive_date:
                announcement.unarchive_announcement()
                messages.success(request, 'Ogłoszenie zostało odarchiwizowane')
            else:
                announcement.archive_announcement()
                messages.success(request, 'Ogłoszenie zostało zarchiwizowane')
        else:
            messages.error(request, 'Nie masz uprawnień do tej akcji')
        return redirect('announcements:announcement_detail', pk=pk)
