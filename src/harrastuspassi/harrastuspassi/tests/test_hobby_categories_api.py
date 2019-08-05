import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_hobby_category_exists(api_client, test_hobby_category):
    test_hobby_category.name = 'Urheilu'
    test_hobby_category.save()
    response = api_client.get(reverse('hobbycategory-list'))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Urheilu'
