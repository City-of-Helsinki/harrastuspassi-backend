import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_location_list_returns_only_editable_for_authenticated_user(user_api_client, user2_api_client, api_client):
    """ Location endpoint should return only editable locations for authenticated user """
    api_url = reverse('location-list')
    response = user_api_client.get(api_url)
    assert response.status_code == 200
    assert len(response.data) == 0

    data_for_user = {'name': 'location for user'}
    response = user_api_client.post(api_url, data_for_user)

    data_for_user2 = {'name': 'location for user 2'}
    response = user2_api_client.post(api_url, data_for_user2)

    # user should not not receive location created by user2
    response = user_api_client.get(api_url)
    assert len(response.data) == 1
    response_json = response.json()[0]
    assert response_json['name'] == data_for_user['name']

    # user2 should not receive location created by user
    response = user2_api_client.get(api_url)
    assert len(response.data) == 1
    response_json = response.json()[0]
    assert response_json['name'] == data_for_user2['name']

    # unauthenticated user should receive both locations
    response = api_client.get(api_url)
    assert len(response.data) == 2
