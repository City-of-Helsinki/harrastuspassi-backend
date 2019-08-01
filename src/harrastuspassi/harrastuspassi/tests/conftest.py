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


@pytest.fixture
def hobbycategory_hierarchy_root():
    root = HobbyCategory.objects.create(name='Ballgames')
    HobbyCategory.objects.create(name='Football', parent=root)
    HobbyCategory.objects.create(name='Tennis', parent=root)
    return root
