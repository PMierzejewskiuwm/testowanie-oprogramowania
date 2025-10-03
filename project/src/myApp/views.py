from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from events.models import Event
from announcements.models import Announcement


class HomeView(TemplateView):
    template_name = 'layout.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pinned_events = Event.objects.filter(is_pinned=True).order_by('-created_at')
        event_paginator = Paginator(pinned_events, self.paginate_by)
        event_page_number = self.request.GET.get('event_page')
        context['event_page_obj'] = event_paginator.get_page(event_page_number)

        pinned_announcements = Announcement.objects.filter(is_pinned=True).order_by('-date')
        announcement_paginator = Paginator(pinned_announcements, self.paginate_by)
        announcement_page_number = self.request.GET.get('announcement_page')
        context['announcement_page_obj'] = announcement_paginator.get_page(announcement_page_number)

        return context

def about(request):
    return render(request, 'about.html')

def paid_service(request):
    return render(request, 'paid_service.html')

def info_help(request):
    return render(request, 'info_help.html')
