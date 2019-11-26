import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from harrastuspassi.models import Benefit, Promotion


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
