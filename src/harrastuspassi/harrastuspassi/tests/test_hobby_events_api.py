import datetime
import pytest
from freezegun import freeze_time
from django.urls import reverse
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.tests.conftest import FROZEN_DATE, FROZEN_DATETIME


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
def test_list_events_filter_by_hobby(api_client, hobby_with_events):
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
    # initialize fixture data to expected values
    set_event_times(hobby_with_events.events.all(), datetime.time(hour=19))
    set_event_times(hobby_with_events2.events.all(), datetime.time(hour=12))
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?start_time_from=18:00&start_time_to=19:00'
    response = api_client.get(url)
    assert response.status_code == 200
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(hobby_with_events.events.values_list('id', flat=True))


@pytest.mark.django_db
def test_list_events_filter_by_category(
    api_client,
    hobby_with_events,
    hobby_with_events2,
    hobby_category
):
    """ HobbyEvents should be filterable by category """
    hobby_with_events.categories.set([hobby_category])
    hobby_with_events.save()
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?category={hobby_category.pk}'
    response = api_client.get(url)
    assert response.status_code == 200
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(hobby_with_events.events.values_list('id', flat=True))


def set_event_times(events, start_time):
    # set list of events to occur at the given time, ending 1 hour after
    for event in events:
        event.start_time = start_time
        event.end_time = start_time.replace(hour=start_time.hour + 1)
        event.save()
    return events


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_filter_by_date(api_client, hobby_with_events, hobby_with_events2, frozen_date):
    """ HobbyEvents should be filterable by start date """
    # initialize fixture data to expected values
    set_event_dates_week_apart(hobby_with_events.events.all(), frozen_date)
    set_event_dates_week_apart(hobby_with_events2.events.all(), frozen_date)
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?start_date_from={FROZEN_DATE}&start_date_to={FROZEN_DATE}'
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2, 'Should return 2 events, one per hobby'
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(HobbyEvent.objects.filter(start_date=frozen_date).values_list('id', flat=True))


def set_event_dates_week_apart(events, start_date):
    # set list of events to occur one week apart beginning from start_date
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
    # initialize fixture data to expected values
    set_event_dates_week_apart(hobby_with_events.events.all(), frozen_date)
    set_event_dates_week_apart(hobby_with_events2.events.all(), frozen_date + datetime.timedelta(days=1))
    day_of_week = frozen_date.isoweekday()
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?start_weekday={day_of_week}'
    response = api_client.get(url)
    assert response.status_code == 200
    event_ids = set(e['id'] for e in response.data)
    assert event_ids == set(hobby_with_events.events.values_list('id', flat=True))


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events_near_point(
    api_client,
    hobby_far_with_events,
    hobby_midway_with_events,
    hobby_near_with_events,
):
    """ HobbyEvents should be orderable by distance to a point """
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?ordering=nearest&near_latitude=1.00000&near_longitude=1.00000'
    response = api_client.get(url)
    assert response.status_code == 200
    events = response.json()
    assert hobby_near_with_events.pk == events[0]['hobby']
    assert hobby_near_with_events.pk == events[1]['hobby']
    assert hobby_midway_with_events.pk == events[2]['hobby']
    assert hobby_midway_with_events.pk == events[3]['hobby']
    assert hobby_far_with_events.pk == events[4]['hobby']
    assert hobby_far_with_events.pk == events[5]['hobby']
    # Reverse
    url = f'{api_url}?ordering=-nearest&near_latitude=1.00000&near_longitude=1.00000'
    response = api_client.get(url)
    assert response.status_code == 200
    events = response.json()
    assert hobby_near_with_events.pk == events[5]['hobby']
    assert hobby_near_with_events.pk == events[4]['hobby']
    assert hobby_midway_with_events.pk == events[3]['hobby']
    assert hobby_midway_with_events.pk == events[2]['hobby']
    assert hobby_far_with_events.pk == events[1]['hobby']
    assert hobby_far_with_events.pk == events[0]['hobby']


@pytest.mark.django_db
def test_hobbyevent_create(user_api_client, valid_hobbyevent_data):
    """ Authenticated user should be able to create a new HobbyEvent """
    url = reverse('hobbyevent-list')
    hobbyevent_count = HobbyEvent.objects.count()
    response = user_api_client.post(url, data=valid_hobbyevent_data, format='json')
    assert response.status_code == 201
    assert HobbyEvent.objects.count() == hobbyevent_count + 1


@pytest.mark.django_db
def test_hobbyevent_unauthenticated_create(api_client, valid_hobbyevent_data):
    """ Unauthenticated user should not be able to create a new HobbyEvent """
    url = reverse('hobbyevent-list')
    hobbyevent_count = HobbyEvent.objects.count()
    response = api_client.post(url, data=valid_hobbyevent_data, format='json')
    assert response.status_code == 401
    assert HobbyEvent.objects.count() == hobbyevent_count


@pytest.mark.django_db
def test_hobbyevent_update(user_api_client, valid_hobbyevent_data):
    """ Authenticated user should be able to edit their HobbyEvents """
    url = reverse('hobbyevent-list')
    response = user_api_client.post(url, data=valid_hobbyevent_data, format='json')
    assert response.status_code == 201
    hobbyevent_data = response.data.copy()
    hobbyevent_data['end_time'] = datetime.datetime.strptime('20:00', '%H:%M').time()
    update_url = reverse('hobbyevent-detail', kwargs={'pk': hobbyevent_data['id']})
    response = user_api_client.put(update_url, data=hobbyevent_data, format='json')
    assert response.status_code == 200
    hobby_obj = HobbyEvent.objects.get(id=response.data['id'])
    assert hobby_obj.end_time == hobbyevent_data['end_time']


@pytest.mark.django_db
def test_hobbyevent_update_unauthenticated_user(user_api_client, api_client, valid_hobbyevent_data):
    """ Authenticated user should not be able to edit someone elses HobbyEvents """
    url = reverse('hobbyevent-list')
    response = user_api_client.post(url, data=valid_hobbyevent_data, format='json')
    assert response.status_code == 201
    hobbyevent_data = response.data.copy()
    hobbyevent_data['end_time'] = datetime.datetime.strptime('21:00', '%H:%M').time()
    update_url = reverse('hobbyevent-detail', kwargs={'pk': hobbyevent_data['id']})
    response = api_client.put(update_url, data=hobbyevent_data, format='json')
    assert response.status_code == 401
    hobbyevent_obj = HobbyEvent.objects.get(id=hobbyevent_data['id'])
    assert hobbyevent_obj.end_time == valid_hobbyevent_data['end_time']


@freeze_time(FROZEN_DATETIME)
@pytest.mark.django_db
def test_list_events_exclude_past_events(api_client, hobby):
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?exclude_past_events=true'
    date_today = datetime.datetime.strptime(FROZEN_DATE, '%Y-%m-%d').date()

    # event ends after a week from now, should be returned from API
    test_event = HobbyEvent.objects.create(
        hobby=hobby,
        start_date=datetime.datetime.strptime('2022-1-1', '%Y-%m-%d').date(),
        end_date=date_today + datetime.timedelta(days=7),
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.strptime('14:59', '%H:%M').time()
    )
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1

    # event ended a minute ago, should not be returned from API
    test_event.end_date = date_today
    test_event.save()
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 0

    # event's end_time is after time now, but date is before
    test_event.end_date = date_today - datetime.timedelta(days=1)
    test_event.end_time = datetime.datetime.strptime('20:00', '%H:%M').time()
    test_event.save()
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 0


@freeze_time(FROZEN_DATETIME)
@pytest.mark.django_db
def test_hobby_event_text_search(
    api_client,
    hobby,
    hobby_with_events,
    hobby_with_events2,
    municipality,
    organizer,
    location
):
    date_today = datetime.datetime.strptime(FROZEN_DATE, '%Y-%m-%d').date()
    api_url = reverse('hobbyevent-list')
    test_hobby_category = HobbyCategory.objects.create(
        name='Saappaanheitto'
    )
    test_hobby = Hobby.objects.create(
        name='Lorem ipsum dolor sit amet',
        description='Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua',
        location=location,
        organizer=organizer,
        municipality=municipality,
    )
    test_hobby.categories.set([test_hobby_category])
    test_event = HobbyEvent.objects.create(
        hobby=test_hobby,
        start_date=datetime.datetime.strptime('2022-1-1', '%Y-%m-%d').date(),
        end_date=date_today + datetime.timedelta(days=7),
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.strptime('14:59', '%H:%M').time()
    )
    # Test searching by name
    url = f'{api_url}?search=lorem ipsum'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert test_hobby.id == response.data[0]['hobby']
    assert test_event.id == response.data[0]['id']

    # Test searching by description
    url = f'{api_url}?search=eiusmod tempor'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert test_hobby.id == response.data[0]['hobby']
    assert test_event.id == response.data[0]['id']

    # Test searching by category
    url = f'{api_url}?search=saappaan'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert test_hobby.id == response.data[0]['hobby']
    assert test_event.id == response.data[0]['id']
