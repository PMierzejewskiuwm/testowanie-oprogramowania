# tests/test_events_views.py
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from events.models import Event

pytestmark = pytest.mark.django_db


class TestEventListView:
    def test_all_non_archived_events(self, client, event, archived_event):
        """Test wyświetlania niearchiwalnych wydarzeń"""
        url = reverse('events:list_event', kwargs={'filter': 'all_non_archived'})
        response = client.get(url)

        assert response.status_code == 200
        events = response.context['events']
        assert len(events) == 1
        assert events[0] == event  # Tylko niearchiwalne

    def test_my_events_authenticated(self, client, user, event):
        """Test 'moje wydarzenia' dla zalogowanego użytkownika"""
        client.force_login(user)
        url = reverse('events:list_event', kwargs={'filter': 'my'})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context['events']) == 1
        assert response.context['is_my_events'] == True

    def test_my_events_unauthenticated(self, client):
        """Test przekierowania dla niezalogowanego użytkownika"""
        url = reverse('events:list_event', kwargs={'filter': 'my'})
        response = client.get(url)

        assert response.status_code == 302
        assert '/login/' in response.url

    def test_search_functionality(self, client, event):
        """Test wyszukiwania"""
        url = reverse('events:list_event', kwargs={'filter': 'all_non_archived'})
        response = client.get(url, {'keyword': 'Test'})

        assert response.status_code == 200
        assert len(response.context['events']) == 1
        assert 'Test' in response.context['events'][0].event_name

    def test_location_filter(self, client, event):
        """Test filtrowania po lokalizacji"""
        url = reverse('events:list_event', kwargs={'filter': 'all_non_archived'})
        response = client.get(url, {'location': 'Warsaw'})

        assert response.status_code == 200
        assert len(response.context['events']) == 1
        assert response.context['events'][0].location == 'Warsaw'

    @pytest.mark.parametrize('sort_by,expected_count', [
        ('event_date', 1),
        ('-event_date', 1),
        ('created_at', 1),
        ('-created_at', 1),
    ])
    def test_sorting_options(self, client, event, sort_by, expected_count):
        """Test różnych opcji sortowania"""
        url = reverse('events:list_event', kwargs={'filter': 'all_non_archived'})
        response = client.get(url, {'sort_by': sort_by})

        assert response.status_code == 200
        assert len(response.context['events']) == expected_count

    def test_context_data(self, client, event):
        """Test danych w kontekście"""
        url = reverse('events:list_event', kwargs={'filter': 'all_non_archived'})
        response = client.get(url)

        context = response.context
        assert context['is_all_events'] == True
        assert context['is_archived'] == False
        assert context['is_my_events'] == False
        assert 'available_locations' in context
        assert 'sort_options' in context
        assert len(context['sort_options']) == 6


class TestEventDetailView:
    def test_event_detail_display(self, client, event):
        """Test wyświetlania szczegółów wydarzenia"""
        url = reverse('events:detail_event', kwargs={'pk': event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['event'] == event
        assert 'comments' in response.context
        assert 'comment_form' in response.context
        assert 'average_rating' in response.context

    def test_event_not_found(self, client):
        """Test nieistniejącego wydarzenia"""
        url = reverse('events:detail_event', kwargs={'pk': 999})
        response = client.get(url)

        assert response.status_code == 404


class TestEventCreateView:
    def test_create_view_authenticated(self, client, user):
        """Test formularza tworzenia dla zalogowanego użytkownika"""
        client.force_login(user)
        url = reverse('events:create_event')
        response = client.get(url)

        assert response.status_code == 200
        assert 'form' in response.context

    def test_create_event_valid_data(self, client, user):
        """Test tworzenia wydarzenia z poprawnymi danymi"""
        client.force_login(user)
        url = reverse('events:create_event')

        data = {
            'event_name': 'Nowe Wydarzenie',
            'description': 'Opis nowego wydarzenia',
            'location': 'Gdansk',
            'event_date': (timezone.now() + timezone.timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse('events:list_event')
        assert Event.objects.filter(event_name='Nowe Wydarzenie').exists()

    def test_create_view_unauthenticated(self, client):
        """Test przekierowania dla niezalogowanego użytkownika"""
        url = reverse('events:create_event')
        response = client.get(url)

        assert response.status_code == 302
        assert '/login/' in response.url


class TestEventUpdateView:
    def test_update_view_owner(self, client, user, event):
        """Test edycji wydarzenia przez właściciela"""
        client.force_login(user)
        url = reverse('events:update_event', kwargs={'pk': event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['object'] == event

    def test_update_event_valid_data(self, client, user, event):
        """Test aktualizacji wydarzenia"""
        client.force_login(user)
        url = reverse('events:update_event', kwargs={'pk': event.pk})

        data = {
            'event_name': 'Zaktualizowane Wydarzenie',
            'description': event.description,
            'location': event.location,
            'event_date': event.event_date.strftime('%Y-%m-%d %H:%M:%S'),
        }

        response = client.post(url, data)

        assert response.status_code == 302
        event.refresh_from_db()
        assert event.event_name == 'Zaktualizowane Wydarzenie'

    def test_update_view_other_user(self, client, event):
        """Test edycji wydarzenia przez innego użytkownika"""
        other_user = User.objects.create_user('otheruser', 'otherpass')
        client.force_login(other_user)

        url = reverse('events:update_event', kwargs={'pk': event.pk})
        response = client.get(url)

        # Powinno zwrócić 403 lub 404
        assert response.status_code in [403, 404]


class TestEventDeleteView:
    def test_delete_view_owner(self, client, user, event):
        """Test potwierdzenia usunięcia przez właściciela"""
        client.force_login(user)
        url = reverse('events:delete_event', kwargs={'pk': event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['object'] == event

    def test_delete_event(self, client, user, event):
        """Test usuwania wydarzenia"""
        client.force_login(user)
        url = reverse('events:delete_event', kwargs={'pk': event.pk})

        response = client.post(url)

        assert response.status_code == 302
        assert not Event.objects.filter(pk=event.pk).exists()

    def test_delete_view_other_user(self, client, event):
        """Test usuwania wydarzenia przez innego użytkownika"""
        other_user = User.objects.create_user('otheruser', 'otherpass')
        client.force_login(other_user)

        url = reverse('events:delete_event', kwargs={'pk': event.pk})
        response = client.post(url)

        # Wydarzenie powinno nadal istnieć
        assert Event.objects.filter(pk=event.pk).exists()
        assert response.status_code in [403, 404]