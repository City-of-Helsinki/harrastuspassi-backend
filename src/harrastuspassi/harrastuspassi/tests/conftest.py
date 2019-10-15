import datetime
import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
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


@pytest.mark.django_db
@pytest.fixture
def user2():
    return get_user_model().objects.create(
        username='test_user2',
        first_name='Athelney',
        last_name='Jones',
        email='athelney.jones@met.police.uk',
    )


@pytest.fixture
def user_api_client(user):
    api_client = APIClient()
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def user2_api_client(user2):
    api_client = APIClient()
    api_client.force_authenticate(user2)
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
        'categories': [hobby_category.id],
        'description': 'Description of a new hobby',
        'location': location.id,
        'name': 'New Hobby',
        'organizer': organizer.id,
    }


#
# Geo fixtures
#

@pytest.fixture
def point_far():
    return Point(8, 10)


@pytest.fixture
def point_midway():
    return Point(6, 4)


@pytest.fixture
def point_near():
    return Point(2, 3)


@pytest.fixture
def point_home():
    return Point(1, 1)


@pytest.fixture
def location_far(point_far):
    return Location.objects.create(name='Farland', coordinates=point_far)


@pytest.fixture
def location_midway(point_midway):
    return Location.objects.create(name='Midwayland', coordinates=point_midway)


@pytest.fixture
def location_near(point_near):
    return Location.objects.create(name='Nearland', coordinates=point_near)


@pytest.fixture
def hobby_far(location_far, organizer):
    return Hobby.objects.create(name='Test Hobby at farland', location=location_far, organizer=organizer)


@pytest.fixture
def hobby_midway(location_midway, organizer):
    return Hobby.objects.create(name='Test Hobby at midwayland', location=location_midway, organizer=organizer)


@pytest.fixture
def hobby_near(location_near, organizer):
    return Hobby.objects.create(name='Test Hobby at nearland', location=location_near, organizer=organizer)


@pytest.fixture
def hobby_far_with_events(hobby_far, frozen_date):
    HobbyEvent.objects.create(hobby=hobby_far, start_date=frozen_date, start_time='18:00',
                              end_date=frozen_date, end_time='19:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=hobby_far, start_date=another_date, start_time='18:00',
                              end_date=another_date, end_time='19:00')
    return hobby_far


@pytest.fixture
def hobby_midway_with_events(hobby_midway, frozen_date):
    HobbyEvent.objects.create(hobby=hobby_midway, start_date=frozen_date, start_time='18:00',
                              end_date=frozen_date, end_time='19:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=hobby_midway, start_date=another_date, start_time='18:00',
                              end_date=another_date, end_time='19:00')
    return hobby_midway


@pytest.fixture
def hobby_near_with_events(hobby_near, frozen_date):
    HobbyEvent.objects.create(hobby=hobby_near, start_date=frozen_date, start_time='18:00',
                              end_date=frozen_date, end_time='19:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=hobby_near, start_date=another_date, start_time='18:00',
                              end_date=another_date, end_time='19:00')
    return hobby_near


