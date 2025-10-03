from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import get_object_or_404

from comments_and_ratings.forms import CommentForm
from .models import Gallery, Photo
from .forms import GalleryForm, PhotoForm
from django.db.models import Q


class GalleryListView(ListView):
    """
    View showing galleries:
    - For logged-in users: all galleries or only user's galleries depending on URL
    - For anonymous users: only all galleries (read-only)
    """
    model = Gallery
    context_object_name = 'galleries'
    paginate_by = 10

    def get_queryset(self):
        queryset = Gallery.objects.all()

        match self.kwargs.get('filter'):
            case 'all':
                pass
            case 'my':
                if not self.request.user.is_authenticated:
                    return Gallery.objects.none()
                queryset = queryset.filter(creator=self.request.user)

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        sort_by = self.request.GET.get('sort_by')
        valid_sort_fields = ['-created_at', 'created_at', '-updated_at']
        queryset = queryset.order_by(sort_by if sort_by in valid_sort_fields else '-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_filter = self.kwargs.get('filter', 'all')
        context['is_all_galleries'] = current_filter == 'all'
        context['is_my_galleries'] = current_filter == 'my'
        context['page_param'] = "page"

        context['sort_options'] = [
            {
                'value': '-created_at',
                'label': 'Najnowsze (domyślnie)',
                'selected': self.request.GET.get('sort_by') == '-created_at'
            },
            {
                'value': 'created_at',
                'label': 'Najstarsze',
                'selected': self.request.GET.get('sort_by') == 'created_at'
            },
            {
                'value': '-updated_at',
                'label': 'Ostatnio edytowane',
                'selected': self.request.GET.get('sort_by') == '-updated_at'
            }
        ]
        if not any(opt['selected'] for opt in context['sort_options']):
            context['sort_options'][0]['selected'] = True

        return context



class GalleryDetailView(DetailView):
    """View showing gallery details"""
    model = Gallery
    context_object_name = 'gallery'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        """Add context for template rendering:
        - gallery (Gallery): The current gallery object.
        - is_owner (bool): True if the logged-in user is the creator of the gallery.
        - is_all_galleries (bool): Always False; used to distinguish from the gallery list view.
        - photos (Page): A paginated list of photos in the gallery.
        - page_obj (Page): The current page of the photo pagination.
        - is_paginated (bool): True if there is more than one page of photos.
        """
        context = super().get_context_data(**kwargs)
        photos = self.object.photos.all().order_by('-uploaded_at')
        context["page_param"] = "page"
        paginator = Paginator(photos, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        gallery = self.object

        content_type = ContentType.objects.get_for_model(gallery)
        object_id = gallery.id

        context['content_type'] = content_type
        context['object_id'] = object_id
        context['comments'] = gallery.comments.filter(parent_comment__isnull=True).order_by('-created_at')
        context['comment_form'] = CommentForm()
        context['average_rating'] = gallery.average_rating
        context['ratings_count'] = gallery.ratings.count()

        if self.request.user.is_authenticated:
            rating_obj = gallery.ratings.filter(user=self.request.user).first()
            context['user_rating'] = rating_obj.rating if rating_obj else None
            context['user_rating_id'] = rating_obj.id if rating_obj else None

        if gallery.average_rating is not None:
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

        context.update({
            'is_owner': self.request.user == self.object.creator,
            'is_all_galleries': False,
            'photos': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages()
        })
        return context


class GalleryCreateView(LoginRequiredMixin, CreateView):
    """
    View allowing to create new gallery.
    Uses Django's generic CreateView.
    """
    model = Gallery
    form_class = GalleryForm
    success_url = reverse_lazy('photo_gallery:gallery_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Galeria została utworzona!")
        return super().form_valid(form)


class GalleryUpdateView(LoginRequiredMixin, UpdateView):
    """
    View managing editing of an existing gallery.
    Uses Django's generic UpdateView.
    """
    model = Gallery
    form_class = GalleryForm
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('photo_gallery:gallery_detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        messages.success(self.request, "Galeria została zaktualizowana!")
        return super().form_valid(form)


class GalleryDeleteView(LoginRequiredMixin, DeleteView):
    """
    View managing deletion of an existing gallery.
    Uses Django's generic DeleteView.
    """
    model = Gallery
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('photo_gallery:user_gallery_list')

    def form_valid(self, form):
        messages.success(self.request, "Galeria została usunięta!")
        return super().form_valid(form)


class PhotoDetailView(DetailView):
    """View showing photo details"""
    model = Photo
    context_object_name = 'photo'

    def get_queryset(self):
        return super().get_queryset().filter(gallery__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = self.object

        content_type = ContentType.objects.get_for_model(photo)
        object_id = photo.id

        context['content_type'] = content_type
        context['object_id'] = object_id
        context['comments'] = photo.comments.filter(parent_comment__isnull=True).order_by('-created_at')
        context['comment_form'] = CommentForm()
        context['average_rating'] = photo.average_rating
        context['ratings_count'] = photo.ratings.count()
        context['is_owner'] = self.request.user == photo.gallery.creator

        if self.request.user.is_authenticated:
            rating_obj = photo.ratings.filter(user=self.request.user).first()
            context['user_rating'] = rating_obj.rating if rating_obj else None
            context['user_rating_id'] = rating_obj.id if rating_obj else None

        if photo.average_rating is not None:
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


class PhotoCreateView(LoginRequiredMixin, CreateView):
    """
    View allowing to create new photo.
    Uses Django's generic CreateView.
    """
    model = Photo
    form_class = PhotoForm

    def dispatch(self, request, *args, **kwargs):
        self.gallery = get_object_or_404(Gallery, slug=kwargs['slug'])
        if self.gallery.creator != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['gallery'] = self.gallery
        return kwargs

    def get_success_url(self):
        return reverse_lazy('photo_gallery:gallery_detail', kwargs={'slug': self.gallery.slug})

    def form_valid(self, form):
        messages.success(self.request, "Zdjęcie zostało dodane do galerii!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery'] = self.gallery
        return context


class PhotoUpdateView(LoginRequiredMixin, UpdateView):
    """
    View managing editing of an existing photo.
    Uses Django's generic UpdateView.
    """
    model = Photo
    form_class = PhotoForm

    def dispatch(self, request, *args, **kwargs):
        self.photo = self.get_object()
        if self.photo.gallery.creator != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['gallery'] = self.photo.gallery
        return kwargs

    def get_success_url(self):
        return reverse_lazy('photo_gallery:gallery_detail', kwargs={'slug': self.photo.gallery.slug})

    def form_valid(self, form):
        messages.success(self.request, "Zdjęcie zostało zaktualizowane!")
        return super().form_valid(form)


class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    """
    View managing deletion of an existing photo.
    Uses Django's generic DeleteView.
    """
    model = Photo

    def dispatch(self, request, *args, **kwargs):
        self.photo = self.get_object()
        if self.photo.gallery.creator != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('photo_gallery:gallery_detail', kwargs={'slug': self.photo.gallery.slug})

    def form_valid(self, form):
        messages.success(self.request, "Zdjęcie zostało usunięte z galerii!")
        return super().form_valid(form)