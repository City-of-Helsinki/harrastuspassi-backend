import datetime
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent, Location, Organizer

FROZEN_DATE = '2022-2-22'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
@pytest.fixture
def user():
    return get_user_model().objects.create(
        username='test_user',
        first_name='James',
        last_name='Doe',
        email='james.doe@foo.com',
    )


@pytest.fixture
def user_api_client(user, api_client):
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def frozen_date():
    year, month, day = map(int, FROZEN_DATE.split('-'))
    return datetime.date(year=year, month=month, day=day)


@pytest.fixture
def location():
    return Location.objects.create(name='Tampere')


@pytest.fixture
def organizer():
    return Organizer.objects.create(name='Sports Club')


@pytest.fixture
def hobby(location, organizer):
    return Hobby.objects.create(name='Test Hobby', location=location, organizer=organizer)


@pytest.fixture
def hobby2(location, organizer):
    return Hobby.objects.create(name='Test Hobby 2', location=location, organizer=organizer)


@pytest.fixture
def hobby_category():
    return HobbyCategory.objects.create(name='Language learning')


@pytest.fixture
def hobbycategory_hierarchy_root():
    root = HobbyCategory.objects.create(name='Ballgames')
    HobbyCategory.objects.create(name='Football', parent=root)
    HobbyCategory.objects.create(name='Tennis', parent=root)
    return root


@pytest.fixture
def hobby_with_events(hobby, frozen_date):
    HobbyEvent.objects.create(hobby=hobby, start_date=frozen_date, start_time='18:00',
                              end_date=frozen_date, end_time='19:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=hobby, start_date=another_date, start_time='18:00',
                              end_date=another_date, end_time='19:00')
    return hobby


@pytest.fixture
def hobby_with_events2(hobby2, frozen_date):
    HobbyEvent.objects.create(hobby=hobby2, start_date=frozen_date, start_time='12:00',
                              end_date=frozen_date, end_time='13:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=hobby2, start_date=another_date, start_time='12:00',
                              end_date=another_date, end_time='13:00')
    return hobby2


@pytest.fixture
def valid_hobby_data(hobby_category, location, organizer):
    """ Valid JSON data for creating a new Hobby """
    return {
        'category': hobby_category.id,
        'description': 'Description of a new hobby',
        'location': location.id,
        'name': 'New Hobby',
        'organizer': organizer.id,
    }
