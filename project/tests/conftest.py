# tests/conftest.py
import os
import sys
import django
from django.conf import settings

# Ścieżka do src
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, '../src')
sys.path.insert(0, SRC_PATH)

PROJECT_NAME = 'myApp'

# Konfiguruj Django
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{PROJECT_NAME}.settings')
    django.setup()

import pytest
from django.contrib.auth.models import User
from events.models import Event
from django.utils import timezone

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def event(db, user):
    return Event.objects.create(
        event_name='Test Event',
        description='Test Description',
        location='Warsaw',
        event_date=timezone.now() + timezone.timedelta(days=7),
        creator=user,
        is_verified=True,
        is_archived=False
    )