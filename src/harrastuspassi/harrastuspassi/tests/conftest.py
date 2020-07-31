import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from harrastuspassi.models import (
    Hobby,
    HobbyCategory,
    HobbyEvent,
    Location,
    Municipality,
    Organizer,
    Promotion,
)

FROZEN_DATE = '2022-2-22'
FROZEN_DATETIME = '2022-2-22 16:00:00'


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


@pytest.mark.django_db
@pytest.fixture
def guardian_anonymous_user():
    return get_user_model().get_anonymous()


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
def frozen_date_plus_year():
    year, month, day = map(int, FROZEN_DATE.split('-'))
    return datetime.date(year=year, month=month, day=day) + datetime.timedelta(365)


@pytest.fixture
def frozen_datetime():
    date_str, time_str = FROZEN_DATETIME.split(' ')
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    return datetime.datetime.combine(
        datetime.date(year=year, month=month, day=day),
        datetime.time(hour=hour, minute=minute, second=second),
    )


@pytest.fixture
def location(municipality):
    return Location.objects.create(name='Tampere', municipality=municipality)


@pytest.fixture
def organizer():
    return Organizer.objects.create(name='Sports Club')


@pytest.fixture
def municipality():
    return Municipality.objects.create(name='Municipality')


@pytest.fixture
def hobby(location, organizer, municipality):
    return Hobby.objects.create(name='Test Hobby', location=location, organizer=organizer, municipality=municipality)


@pytest.fixture
def hobbyevent(hobby):
    return HobbyEvent.objects.create(
        hobby=hobby,
        start_date='2019-01-01',
        end_date='2019-01-01',
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.strptime('10:30', '%H:%M').time()
    )


@pytest.fixture
def hobby2(location, organizer, municipality):
    return Hobby.objects.create(name='Test Hobby 2', location=location, organizer=organizer, municipality=municipality)


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
        'price_type': Hobby.TYPE_FREE,
        'price_amount': 0
    }


@pytest.fixture
def valid_hobbyevent_data(hobby_far):
    """ Valid JSON data for creating a new HobbyEvent """
    return {
        'hobby': hobby_far.id,
        'start_date': '2019-06-01',
        'end_date': '2019-07-01',
        'start_time': datetime.datetime.strptime('14:30', '%H:%M').time(),
        'end_time': datetime.datetime.strptime('16:30', '%H:%M').time()
    }


@pytest.fixture
def valid_benefit_data(promotion):
    """ Valid JSON data for creating a new Benefit object """
    return {
        'promotion': promotion.pk
    }


@pytest.fixture
def valid_promotion_data(frozen_date, organizer, location):
    return {
        'name': 'Test promotion',
        'description': 'Hello this is valid test promotion',
        'start_date': frozen_date,
        'start_time': '15:00',
        'end_date': frozen_date,
        'end_time': '17:00',
        'organizer': organizer.pk,
        'available_count': 10,
        'used_count': 0,
        'location': location.pk
    }


@pytest.fixture
def promotion(frozen_date, municipality, organizer, location):
    return Promotion.objects.create(
        name='Test promotion',
        description='Hello this is test promotion',
        start_date=frozen_date,
        start_time='14:00',
        end_date=frozen_date,
        end_time='16:00',
        municipality=municipality,
        organizer=organizer,
        available_count=10,
        used_count=0,
        location=location
    )


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
def location_data_without_coordinates():
    return {
        'name': 'Kalevan uimahalli',
        'address': 'Sammonkatu 64',
        'zip_code': '33540',
        'city': 'Tampere'
    }


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


@pytest.fixture
def promotion_far(location_far, organizer, frozen_date):
    return Promotion.objects.create(name='Test Promotion at farland',
                                    available_count=100,
                                    location=location_far,
                                    organizer=organizer,
                                    start_date=frozen_date,
                                    start_time='00:00',
                                    end_date=frozen_date + datetime.timedelta(365),
                                    end_time='00:00')


@pytest.fixture
def promotion_midway(location_midway, organizer, frozen_date):
    return Promotion.objects.create(name='Test Promotion at midland',
                                    available_count=100,
                                    location=location_midway,
                                    organizer=organizer,
                                    start_date=frozen_date,
                                    start_time='00:00',
                                    end_date=frozen_date + datetime.timedelta(365),
                                    end_time='00:00')


@pytest.fixture
def promotion_near(location_near, organizer, frozen_date):
    return Promotion.objects.create(name='Test Promotion at nearland',
                                    available_count=100,
                                    location=location_near,
                                    organizer=organizer,
                                    start_date=frozen_date,
                                    start_time='00:00',
                                    end_date=frozen_date + datetime.timedelta(365),
                                    end_time='00:00')
