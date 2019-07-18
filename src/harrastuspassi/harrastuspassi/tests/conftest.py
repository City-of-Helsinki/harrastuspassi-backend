import pytest
from rest_framework.test import APIClient

from harrastuspassi.models import Hobby, Location


@pytest.fixture
def api_client():
  return APIClient()


@pytest.fixture
def test_hobby():
  location = Location.objects.create(name='Testilokaatio')
  return Hobby.objects.create(name='Testiharrastus', day_of_week=1, location=location)
