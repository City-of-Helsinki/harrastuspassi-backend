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