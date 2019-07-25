import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_hobby_exists(api_client, test_hobby):
  test_hobby.name = 'Jalkapallo'
  test_hobby.save()
  response = api_client.get(reverse('hobby-list'))
  assert response.status_code == 200
  assert len(response.data) == 1
  assert response.data[0]['name'] == 'Jalkapallo'


@pytest.mark.django_db
def test_hobby_details(api_client, test_hobby):
  test_hobby.name = 'Jääkiekko'
  test_hobby.save()
  response = api_client.get(reverse('hobby-detail', kwargs={'pk': test_hobby.pk}))
  assert response.status_code == 200
  assert response.data['name'] == 'Jääkiekko'