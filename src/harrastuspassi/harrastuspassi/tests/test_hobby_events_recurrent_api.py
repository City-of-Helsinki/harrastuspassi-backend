import datetime
import pytest
from freezegun import freeze_time
from django.urls import reverse
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.tests.conftest import FROZEN_DATE, FROZEN_DATETIME


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_weeks(user_api_client, hobby_with_events, frozen_date):
    """ With 5 weeks and one day api should create 2 events with 2 weeks delta and 5 with one week """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobby_with_events.pk})
    end_date = frozen_date + datetime.timedelta(weeks=5, days=1)
    response = user_api_client.post(url, { "weeks": 2, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 2
    end_date = frozen_date + datetime.timedelta(weeks=5, days=1)
    response = user_api_client.post(url, { "weeks": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 5
    url = reverse('hobbyevent-detail', kwargs={'pk': hobby_with_events.pk})
    response = user_api_client.get(url)
    assert response.status_code == 200


@freeze_time(FROZEN_DATE)
@pytest.mark.django_db
def test_hobbyevent_recursion_weeks_limits(user_api_client, hobby_with_events, frozen_date):
    """ For exact 3 weeks api should create 3 events and one less when a day is decreased """
    url = reverse('hobbyevent-recurrent', kwargs={'pk': hobby_with_events.pk})
    end_date = frozen_date + datetime.timedelta(weeks=3)
    response = user_api_client.post(url, { "weeks": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 3
    end_date = frozen_date + datetime.timedelta(weeks=3, days=-1)
    response = user_api_client.post(url, { "weeks": 1, "end_date": end_date.isoformat() })
    assert response.status_code == 200
    assert len(response.data['events']) == 2
    url = reverse('hobbyevent-detail', kwargs={'pk': hobby_with_events.pk})
    response = user_api_client.get(url)
    assert response.status_code == 200

