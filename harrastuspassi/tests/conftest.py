import pytest
from rest_framework.test import APIClient

from harrastuspassi.models import Hobby, Location, HobbyCategory


@pytest.fixture
def api_client():
  return APIClient()


@pytest.fixture
def test_hobby():
  location = Location.objects.create(name='Testilokaatio')
  return Hobby.objects.create(name='Testiharrastus', location=location)


@pytest.fixture
def test_hobby_category():
  return HobbyCategory.objects.create(name='Kielten opiskelu')