import datetime
import pytest
from rest_framework.test import APIClient

from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent, Location

FROZEN_DATE = '2022-2-22'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def frozen_date():
    year, month, day = map(int, FROZEN_DATE.split('-'))
    return datetime.date(year=year, month=month, day=day)


@pytest.fixture
def test_location():
    return Location.objects.create(name='Tampere')


@pytest.fixture
def test_hobby(test_location):
    return Hobby.objects.create(name='Test Hobby', location=test_location)


@pytest.fixture
def test_hobby2(test_location):
    return Hobby.objects.create(name='Test Hobby 2', location=test_location)


@pytest.fixture
def test_hobby_category():
    return HobbyCategory.objects.create(name='Language learning')


@pytest.fixture
def hobbycategory_hierarchy_root():
    root = HobbyCategory.objects.create(name='Ballgames')
    HobbyCategory.objects.create(name='Football', parent=root)
    HobbyCategory.objects.create(name='Tennis', parent=root)
    return root


@pytest.fixture
def hobby_with_events(test_hobby, frozen_date):
    HobbyEvent.objects.create(hobby=test_hobby, start_date=frozen_date, start_time='18:00',
                              end_date=frozen_date, end_time='19:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=test_hobby, start_date=another_date, start_time='18:00',
                              end_date=another_date, end_time='19:00')
    return test_hobby


@pytest.fixture
def hobby_with_events2(test_hobby2, frozen_date):
    HobbyEvent.objects.create(hobby=test_hobby2, start_date=frozen_date, start_time='12:00',
                              end_date=frozen_date, end_time='13:00')
    another_date = frozen_date + datetime.timedelta(days=7)
    HobbyEvent.objects.create(hobby=test_hobby2, start_date=another_date, start_time='12:00',
                              end_date=another_date, end_time='13:00')
    return test_hobby2
