import pytest
from django.urls import reverse
from rest_framework.exceptions import ErrorDetail
from harrastuspassi.models import Location


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


@pytest.mark.django_db
def test_geocoding_functionality(user_api_client, user2_api_client, api_client, location_data_without_coordinates):
    """ Posting a location to API without coordinates should fetch the coordinates from Google Geolocoding API """
    api_url = reverse('location-list')
    response = user_api_client.post(api_url, data=location_data_without_coordinates, format='json')
    assert response.status_code == 201
    assert response.data['name'] == location_data_without_coordinates['name']
    assert response.data['coordinates']

    # Creating a location with user provided coordinates should still be possible
    Location.objects.all().delete()
    location_data_with_coordinates = location_data_without_coordinates.copy()
    location_data_with_coordinates['coordinates'] = {
        'type': 'Point',
        'coordinates': [1, 1]
    }
    response = user_api_client.post(api_url, data=location_data_with_coordinates, format='json')
    assert response.status_code == 201
    assert response.data['coordinates']['coordinates'] == [1.0, 1.0]

    # Geocoding a faulty address should fail gracefully
    location_data_without_coordinates['address'] = 'Sangen kelvoton osoite'
    location_data_without_coordinates['city'] = 'Tuskin kaupunki'
    location_data_without_coordinates['zip_code'] = '00000'

    response = user_api_client.post(api_url, data=location_data_without_coordinates, format='json')
    assert response.status_code == 400
    expected_error = [
        ErrorDetail(
            string='This address could not be geocoded. Please confirm your address is right, or try again later.',
            code='invalid')
    ]
    assert response.data == expected_error
