import pytest
from django.urls import reverse
from harrastuspassi.models import HobbyCategory


@pytest.mark.django_db
def test_hobby_category_exists(api_client, test_hobby_category):
    test_hobby_category.name = 'Urheilu'
    test_hobby_category.save()
    response = api_client.get(reverse('hobbycategory-list'))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Urheilu'


@pytest.mark.django_db
def test_hobby_category_include_children(api_client, test_hobby_category):
    child = HobbyCategory.objects.create(name="child", parent=test_hobby_category)
    grand_child = HobbyCategory.objects.create(name="grand_child", parent=child)
    api_url = reverse('hobbycategory-detail', kwargs={'pk': test_hobby_category.pk})
    url = f"{api_url}?include=child_categories"
    response = api_client.get(url)
    assert response.data['id'] == test_hobby_category.pk
    assert response.data['child_categories'][0]['id'] == child.pk
    assert response.data['child_categories'][0]['child_categories'][0]['id'] == grand_child.pk

