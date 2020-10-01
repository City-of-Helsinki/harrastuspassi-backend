import datetime
import pytest
from freezegun import freeze_time
from django.urls import reverse
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.tests.conftest import FROZEN_DATE, FROZEN_DATETIME


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_list_events(api_client, hobby, hobby_with_events):
    """
    HobbyEvents should be listable. Listing events should return only one event per hobby.
    """
    url = reverse('hobbyevent-list')
    response = api_client.get(url)
    assert response.status_code == 200
    # although there are multiple events attached to a hobby,
    # only next one should be returned
    assert len(response.data) == 1


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
    assert event_ids == {hobby_with_events.next_event.pk}


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
    assert event_ids == {hobby_with_events.next_event.pk}


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
    assert event_ids == {hobby_with_events.next_event.pk}


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
    assert hobby_midway_with_events.pk == events[1]['hobby']
    assert hobby_far_with_events.pk == events[2]['hobby']
    # Reverse
    url = f'{api_url}?ordering=-nearest&near_latitude=1.00000&near_longitude=1.00000'
    response = api_client.get(url)
    assert response.status_code == 200
    events = response.json()
    assert hobby_near_with_events.pk == events[2]['hobby']
    assert hobby_midway_with_events.pk == events[1]['hobby']
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
    hobby.next_event = test_event
    hobby.save()
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
        name_fi='Saappaanheitto',
        name_en='Boot throwing',
        name_sv='Startkast'
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
    test_hobby.next_event = test_event
    test_hobby.save()
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

    # Test searching by category name_fi
    url = f'{api_url}?search=saappaan'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert test_hobby.id == response.data[0]['hobby']
    assert test_event.id == response.data[0]['id']

    # Test searching by category name_en
    url = f'{api_url}?search=boot'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert test_hobby.id == response.data[0]['hobby']
    assert test_event.id == response.data[0]['id']

    # Test searching by category name_sv
    url = f'{api_url}?search=star'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert test_hobby.id == response.data[0]['hobby']
    assert test_event.id == response.data[0]['id']


@pytest.mark.django_db
def test_price_type_filter(user_api_client, location, organizer, municipality):
    url = reverse('hobbyevent-list')
    free_type_hobby = Hobby.objects.create(
        name='Free type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_FREE
    )
    free_type_hobby_event = HobbyEvent.objects.create(
        hobby=free_type_hobby,
        start_date=datetime.datetime(2020, 5, 17),
        end_date=datetime.datetime(2020, 5, 17),
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now()
    )
    free_type_hobby.next_event = free_type_hobby_event
    free_type_hobby.save()
    annual_type_hobby = Hobby.objects.create(
        name='Annual type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_ANNUAL
    )
    annual_type_hobby_event = HobbyEvent.objects.create(
        hobby=annual_type_hobby,
        start_date=datetime.datetime(2020, 5, 17),
        end_date=datetime.datetime(2020, 5, 17),
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now()
    )
    annual_type_hobby.next_event = annual_type_hobby_event
    annual_type_hobby.save()
    seasonal_type_hobby = Hobby.objects.create(
        name='Seasonal type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_SEASONAL
    )
    seasonal_type_hobby_event = HobbyEvent.objects.create(
        hobby=seasonal_type_hobby,
        start_date=datetime.datetime(2020, 5, 17),
        end_date=datetime.datetime(2020, 5, 17),
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now()
    )
    seasonal_type_hobby.next_event = seasonal_type_hobby_event
    seasonal_type_hobby.save()
    one_time_type_hobby = Hobby.objects.create(
        name='One time type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_ONE_TIME
    )
    one_time_type_hobby_event = HobbyEvent.objects.create(
        hobby=one_time_type_hobby,
        start_date=datetime.datetime(2020, 5, 17),
        end_date=datetime.datetime(2020, 5, 17),
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.now()
    )
    one_time_type_hobby.next_event = one_time_type_hobby_event
    one_time_type_hobby.save()
    response = user_api_client.get(url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 4

    # Filter for hobby events with price type of free
    url_with_free_filter = f'{url}?price_type={Hobby.TYPE_FREE}'
    response = user_api_client.get(url_with_free_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['hobby'] == free_type_hobby.id

    # Filter for hobby events with price type of annual
    url_with_annual_filter = f'{url}?price_type={Hobby.TYPE_ANNUAL}'
    response = user_api_client.get(url_with_annual_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['hobby'] == annual_type_hobby.id

    # Filter for hobby events with price type of seasonal
    url_with_seasonal_filter = f'{url}?price_type={Hobby.TYPE_SEASONAL}'
    response = user_api_client.get(url_with_seasonal_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['hobby'] == seasonal_type_hobby.id

    # Filter for hobby events with price type of one_time
    url_with_one_time_filter = f'{url}?price_type={Hobby.TYPE_ONE_TIME}'
    response = user_api_client.get(url_with_one_time_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['hobby'] == one_time_type_hobby.id


@pytest.mark.django_db
def test_hobby_event_recurrence(user_api_client, valid_hobbyevent_data):
    url = reverse('hobbyevent-list')
    valid_hobbyevent_data['is_recurrent'] = True
    valid_hobbyevent_data['recurrency_count'] = 2
    assert HobbyEvent.objects.count() == 0
    response = user_api_client.post(url, valid_hobbyevent_data, format='json')
    assert response.status_code == 201
    assert HobbyEvent.objects.count() == 3
    assert HobbyEvent.objects.filter(recurrence_start_event=response.data['id']).count() == 2


@pytest.mark.django_db
def test_hobby_event_search(user_api_client, hobby_with_events):
    """
    Custom HobbyEventSearchFilter should include category's descendants in the queryset.
    """
    api_url = reverse('hobbyevent-list')
    parent_category = HobbyCategory.objects.create(
        name_fi='Yleisurheilu'
    )
    child_category = HobbyCategory.objects.create(
        name_fi='Kuulantyöntö',
        parent=parent_category
    )
    hobby_with_events.categories.add(child_category)
    url = f'{api_url}?search=yleisurheilu'
    response = user_api_client.get(url)
    assert len(response.data) == 1


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobby_event_api_returns_next_event(user_api_client, hobby):
    """ HobbyEvent endpoint should only return next event """
    url = reverse('hobbyevent-list')
    tomorrow = datetime.datetime.strptime(FROZEN_DATE, '%Y-%m-%d').date() + datetime.timedelta(days=1)
    day_after_tomorrow = datetime.datetime.strptime(FROZEN_DATE, '%Y-%m-%d').date() + datetime.timedelta(days=2)
    next_event = HobbyEvent.objects.create(
        hobby=hobby,
        start_date=tomorrow,
        start_time='16:00',
        end_date=tomorrow,
        end_time='17:45'
    )
    HobbyEvent.objects.create(
        hobby=hobby,
        start_date=day_after_tomorrow,
        start_time='16:00',
        end_date=day_after_tomorrow,
        end_time='17:45'
    )
    hobby.next_event = next_event
    hobby.save()
    response = user_api_client.get(url)
    assert len(response.data) == 1
    assert response.data[0]['id'] == next_event.pk


@freeze_time(FROZEN_DATETIME)
@pytest.mark.django_db
def test_hobbyevent_start_date_ordering(api_client, hobby, hobby2, hobby3):
    """ HobbyEvents should be orderable by start_date """
    date_today = datetime.datetime.strptime(FROZEN_DATE, '%Y-%m-%d').date()
    hobbyevent_first = HobbyEvent.objects.create(
        hobby=hobby,
        start_date=date_today,
        end_date=date_today,
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.strptime('10:30', '%H:%M').time()
    )
    hobby.next_event = hobbyevent_first
    hobby.save()
    hobbyevent_second = HobbyEvent.objects.create(
        hobby=hobby2,
        start_date=date_today + datetime.timedelta(days=7),
        end_date=date_today + datetime.timedelta(days=7),
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.strptime('10:30', '%H:%M').time()
    )
    hobby2.next_event = hobbyevent_second
    hobby2.save()
    hobbyevent_third = HobbyEvent.objects.create(
        hobby=hobby3,
        start_date=date_today + datetime.timedelta(days=14),
        end_date=date_today + datetime.timedelta(days=14),
        start_time=datetime.datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.datetime.strptime('10:30', '%H:%M').time()
    )
    hobby3.next_event = hobbyevent_third
    hobby3.save()
    api_url = reverse('hobbyevent-list')
    url = f'{api_url}?ordering=start_date'
    response = api_client.get(url)
    assert response.status_code == 200
    assert hobbyevent_first.pk == response.data[0]['id']
    assert hobbyevent_second.pk == response.data[1]['id']
    assert hobbyevent_third.pk == response.data[2]['id']
    # Reverse
    url = f'{api_url}?ordering=-start_date'
    response = api_client.get(url)
    assert response.status_code == 200
    assert hobbyevent_first.pk == response.data[2]['id']
    assert hobbyevent_second.pk == response.data[1]['id']
    assert hobbyevent_third.pk == response.data[0]['id']
