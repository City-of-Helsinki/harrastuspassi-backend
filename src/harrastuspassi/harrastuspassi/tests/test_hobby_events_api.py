import datetime
import pytest
from freezegun import freeze_time
from django.urls import reverse
from harrastuspassi.models import HobbyEvent
from harrastuspassi.tests.conftest import FROZEN_DATE


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events(api_client, hobby_with_events):
    """ HobbyEvents should be listable """
    url = reverse('hobbyevent-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == hobby_with_events.events.count()


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_filter_by_hobby(api_client, hobby_with_events, hobby_with_events2):
    """ HobbyEvents should be filterable by Hobby id """
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?hobby={hobby_with_events.pk}'
    response = api_client.get(url)
    assert response.status_code == 200
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(hobby_with_events.events.values_list('id', flat=True))


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_filter_by_time(api_client, hobby_with_events, hobby_with_events2):
    """ HobbyEvents should be filterable by start time """
    set_event_times(hobby_with_events.events.all(), datetime.time(hour=19))
    set_event_times(hobby_with_events2.events.all(), datetime.time(hour=12))
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?start_time_from=18:00&start_time_to=19:00'
    response = api_client.get(url)
    assert response.status_code == 200
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(hobby_with_events.events.values_list('id', flat=True))


def set_event_times(events, start_time):
    for event in events:
        event.start_time = start_time
        event.end_time = start_time.replace(hour=start_time.hour + 1)
        event.save()
    return events


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_filter_by_date(api_client, hobby_with_events, hobby_with_events2, frozen_date):
    """ HobbyEvents should be filterable by start date """
    set_event_dates(hobby_with_events.events.all(), frozen_date)
    set_event_dates(hobby_with_events2.events.all(), frozen_date)
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?start_date_from={FROZEN_DATE}&start_date_to={FROZEN_DATE}'
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2, 'Should return 2 events, one per hobby'
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(HobbyEvent.objects.filter(start_date=frozen_date).values_list('id', flat=True))


def set_event_dates(events, start_date):
    counter = 0
    for event in events:
        date = start_date + datetime.timedelta(days=counter * 7)
        event.start_date = date
        event.end_date = date
        event.save()
        counter += 1
    return events


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_include_hobby_detail(api_client, hobby_with_events, frozen_date):
    """ HobbyEvents should have full Hobby data available with optional include parameter """
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?include=hobby_detail'
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]['hobby']['name'] == hobby_with_events.name, 'Response should include full hobby data'


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_filter_by_weekday(api_client, hobby_with_events, hobby_with_events2, frozen_date):
    """ HobbyEvents should be filterable by ISO weekday based on start_date """
    set_event_dates(hobby_with_events.events.all(), frozen_date)
    set_event_dates(hobby_with_events2.events.all(), frozen_date + datetime.timedelta(days=1))
    day_of_week = frozen_date.isoweekday()
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?start_weekday={day_of_week}'
    response = api_client.get(url)
    assert response.status_code == 200
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(hobby_with_events.events.values_list('id', flat=True))
