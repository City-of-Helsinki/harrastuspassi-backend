import datetime
import pytest
from freezegun import freeze_time
from django.urls import reverse
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.tests.conftest import FROZEN_DATE, FROZEN_DATETIME


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_weeks(user_api_client, hobbyevent2, frozen_date):
    """ Test that with weeks endpoint creates correct ammount of events """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobbyevent2.pk})
    end_date = frozen_date + datetime.timedelta(weeks=5, days=1)
    response = user_api_client.post(url, { "weeks": 2, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 2
    end_date = frozen_date + datetime.timedelta(weeks=5, days=1)
    response = user_api_client.post(url, { "weeks": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 5
    url = reverse('hobbyevent-detail', kwargs={'pk': hobbyevent2.pk})
    response = user_api_client.get(url)
    assert response.status_code == 200


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_weeks_limits(user_api_client, hobbyevent2, frozen_date):
    """ Recurring events should have limits so that event stating with given end date should be created """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobbyevent2.pk})
    end_date = frozen_date + datetime.timedelta(weeks=3)
    response = user_api_client.post(url, { "weeks": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 3
    end_date = frozen_date + datetime.timedelta(weeks=3, days=-1)
    response = user_api_client.post(url, { "weeks": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 2
    url = reverse('hobbyevent-detail', kwargs={'pk': hobbyevent2.pk})
    response = user_api_client.get(url)
    assert response.status_code == 200


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_days(user_api_client, hobbyevent2, frozen_date):
    """ Test that given day ammount gives correct ammount of events """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobbyevent2.pk})
    end_date = frozen_date + datetime.timedelta(days=8)
    response = user_api_client.post(url, { "days": 3, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 2
    end_date = frozen_date + datetime.timedelta(days=7)
    response = user_api_client.post(url, { "days": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 7
    url = reverse('hobbyevent-detail', kwargs={'pk': hobbyevent2.pk})
    response = user_api_client.get(url)
    assert response.status_code == 200


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_days_limits(user_api_client, hobbyevent2, frozen_date):
    """ Repeated event starting with last given date should be created """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobbyevent2.pk})
    end_date = frozen_date + datetime.timedelta(days=10)
    response = user_api_client.post(url, { "days": 5, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 2
    end_date = frozen_date + datetime.timedelta(days=9)
    response = user_api_client.post(url, { "days": 5, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 1
    url = reverse('hobbyevent-detail', kwargs={'pk': hobbyevent2.pk})
    response = user_api_client.get(url)
    assert response.status_code == 200


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_maximum(user_api_client, hobbyevent2, frozen_date):
    """ Test that recursion endpoint fails when user is trying to create too many events """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobbyevent2.pk})
    end_date = frozen_date + datetime.timedelta(days=50)
    response = user_api_client.post(url, { "days": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 50
    end_date = frozen_date + datetime.timedelta(days=51)
    response = user_api_client.post(url, { "days": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 400

