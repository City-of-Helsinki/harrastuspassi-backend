import pytest
from django.urls import reverse
from harrastuspassi.models import Organizer


@pytest.mark.django_db
def test_organizer_list_returns_only_editable_for_authenticated_user(user_api_client, user2_api_client, api_client):
    """ Organizer endpoint should return only editable organizers for authenticated user """
    api_url = reverse('organizer-list')
    response = user_api_client.get(api_url)
    assert response.status_code == 200
    assert len(response.data) == 0

    data_for_user = {'name': 'organizer for user'}
    response = user_api_client.post(api_url, data_for_user)

    data_for_user2 = {'name': 'organizer for user 2'}
    response = user2_api_client.post(api_url, data_for_user2)

    # user should not not receive organizer created by user2
    response = user_api_client.get(api_url)
    assert len(response.data) == 1
    response_json = response.json()[0]
    assert response_json['name'] == data_for_user['name']

    # user2 should not receive organizer created by user
    response = user2_api_client.get(api_url)
    assert len(response.data) == 1
    response_json = response.json()[0]
    assert response_json['name'] == data_for_user2['name']

    # unauthenticated user should receive both organizers
    response = api_client.get(api_url)
    assert len(response.data) == 2
