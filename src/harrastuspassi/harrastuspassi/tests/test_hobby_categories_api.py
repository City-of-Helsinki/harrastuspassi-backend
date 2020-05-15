import pytest
from django.urls import reverse
from harrastuspassi.models import HobbyCategory


@pytest.mark.django_db
def test_hobby_category_exists(api_client, hobby_category):
    hobby_category.name = 'Urheilu'
    hobby_category.save()
    response = api_client.get(reverse('hobbycategory-list'))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Urheilu'


@pytest.mark.django_db
def test_hobby_category_include_children(api_client, hobby_category):
    """ Include parameter should allow serialization of full child category data """
    child = HobbyCategory.objects.create(name="child", parent=hobby_category)
    grand_child = HobbyCategory.objects.create(name="grand_child", parent=child)
    api_url = reverse('hobbycategory-detail', kwargs={'pk': hobby_category.pk})
    url = f"{api_url}?include=child_categories"
    response = api_client.get(url)
    assert response.data['id'] == hobby_category.pk
    assert response.data['child_categories'][0]['id'] == child.pk
    assert response.data['child_categories'][0]['child_categories'][0]['id'] == grand_child.pk


@pytest.mark.django_db
def test_hobby_category_parent_filter_null(api_client, hobbycategory_hierarchy_root):
    """ Category listing should be filterable to include only root categories """
    api_url = reverse('hobbycategory-list')
    url = f"{api_url}?parent=null"
    response = api_client.get(url)
    assert len(response.data) == 1
    assert response.data[0]['id'] == hobbycategory_hierarchy_root.pk


@pytest.mark.django_db
def test_hobby_category_parent_filter_pk(api_client, hobbycategory_hierarchy_root):
    """ Category listing should be filterable to include only root categories """
    api_url = reverse('hobbycategory-list')
    url = f"{api_url}?parent={hobbycategory_hierarchy_root.pk}"
    response = api_client.get(url)
    assert len(response.data) == hobbycategory_hierarchy_root.get_children().count()
    response_category_ids = set([c['id'] for c in response.data])
    assert response_category_ids == set([c.pk for c in hobbycategory_hierarchy_root.get_children()])


@pytest.mark.django_db
def test_hobby_category_translations(api_client):
    """ Category name should be changed to translated versions based on query param """
    api_url = reverse('hobbycategory-list')
    api_url_en = f'{api_url}?lang=en'
    api_url_fi = f'{api_url}?lang=fi'
    api_url_sv = f'{api_url}?lang=sv'

    assert HobbyCategory.objects.count() == 0

    category = HobbyCategory.objects.create(
        name='Jalkapallo',
        name_fi='Jalkapallo suomeksi',
        name_en='Jalkapallo englanniksi',
        name_sv='Jalkapallo ruotsiksi'
    )

    response = api_client.get(api_url)
    assert response.data[0]['name'] == category.name

    response = api_client.get(api_url_fi)
    assert response.data[0]['name'] == category.name_fi

    response = api_client.get(api_url_en)
    assert response.data[0]['name'] == category.name_en

    response = api_client.get(api_url_sv)
    assert response.data[0]['name'] == category.name_sv
