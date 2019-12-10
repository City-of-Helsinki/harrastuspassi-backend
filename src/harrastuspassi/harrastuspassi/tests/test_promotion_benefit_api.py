import datetime
import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from freezegun import freeze_time
from harrastuspassi.models import Benefit, Promotion
from harrastuspassi.tests.conftest import FROZEN_DATE, FROZEN_DATETIME


@pytest.mark.django_db
def test_promotion_create(user_api_client, valid_promotion_data):
    """ Authenticated user should be able to create a new promotion """
    url = reverse('promotion-list')
    promotion_count = Promotion.objects.count()
    response = user_api_client.post(url, data=valid_promotion_data, format='json')
    assert response.status_code == 201
    assert Promotion.objects.count() == promotion_count + 1


@pytest.mark.django_db
def test_promotion_create_as_municipality_moderator(user_api_client, valid_promotion_data, user, municipality):
    url = reverse('promotion-list')
    municipality.moderators.add(user)
    response = user_api_client.post(url, data=valid_promotion_data, format='json')
    assert response.status_code == 201
    assert Promotion.objects.count() == 1
    latest_promotion = Promotion.objects.all()[0]
    assert latest_promotion.municipality_id == municipality.pk


@pytest.mark.django_db
def test_promotion_available_count(user_api_client, promotion, valid_benefit_data):
    """ It should only be possible to use this promotion once """
    promotion.available_count = 1
    promotion.used_count = 0
    promotion.save()
    # Using the last promotion by creating a new benefit
    url = reverse('benefit-list')
    response = user_api_client.post(url, data=valid_benefit_data, format='json')
    assert response.status_code == 201
    # Trying to exceed promotion available count will raise ValidationError
    url = reverse('benefit-list')
    response = user_api_client.post(url, data=valid_benefit_data, format='json')
    assert response.status_code == 400
    assert response.data['non_field_errors'][0].code == 'invalid'


@pytest.mark.django_db
def test_benefit_api_unauthenticated_user(api_client, valid_benefit_data):
    """ Unauthenticated users should not be able to create a new benefit """
    url = reverse('benefit-list')
    benefit_count = Benefit.objects.count()
    response = api_client.post(url, data=valid_benefit_data, format='json')
    assert response.status_code == 401
    assert Benefit.objects.count() == benefit_count


@pytest.mark.django_db
def test_benefit_api_authenticated_user(user_api_client, valid_benefit_data):
    """ Authenticated users should be able to create a new benefit """
    url = reverse('benefit-list')
    response = user_api_client.post(url, data=valid_benefit_data, format='json')
    assert response.status_code == 201


@freeze_time(FROZEN_DATETIME)
@pytest.mark.django_db
def test_list_promotions_exclude_past_events(api_client, organizer, location):
    api_url = reverse('promotion-list')
    url = f'{api_url}?exclude_past_events=true'
    Promotion.objects.all().delete()
    date_today = datetime.datetime.strptime(FROZEN_DATE, '%Y-%m-%d').date()

    # event ends after a week from now, should be returned from API
    test_event = Promotion.objects.create(
        name='Test promotion',
        description='Hello this is valid test promotion',
        start_date=FROZEN_DATE,
        start_time='10:00',
        end_date=date_today + datetime.timedelta(days=7),
        end_time='15:59',
        organizer=organizer,
        available_count=10,
        used_count=0,
        location=location
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
    test_event.end_time = datetime.datetime.strptime('22:00', '%H:%M').time()
    test_event.save()
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 0
