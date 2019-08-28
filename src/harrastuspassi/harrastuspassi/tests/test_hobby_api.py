import pytest
from django.urls import reverse
from harrastuspassi.models import Hobby


@pytest.mark.django_db
def test_hobby_exists(api_client, hobby):
    hobby.name = 'Jalkapallo'
    hobby.save()
    response = api_client.get(reverse('hobby-list'))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Jalkapallo'


@pytest.mark.django_db
def test_hobby_details(api_client, hobby):
    hobby.name = 'Jääkiekko'
    hobby.save()
    response = api_client.get(reverse('hobby-detail', kwargs={'pk': hobby.pk}))
    assert response.status_code == 200
    assert response.data['name'] == 'Jääkiekko'


@pytest.mark.django_db
def test_hobby_category_filter(api_client, hobbycategory_hierarchy_root):
    """ Hobbies should be filterable by category id """
    first_category = hobbycategory_hierarchy_root.get_children().first()
    last_category = hobbycategory_hierarchy_root.get_children().last()
    assert first_category != last_category, "test data is invalid, there should be multiple child categories"
    some_hobby = Hobby.objects.create(name="some hobby", category=first_category)
    Hobby.objects.create(name="another hobby", category=last_category)

    response = api_client.get(reverse('hobby-list'), {'category': first_category.id})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == some_hobby.name


@pytest.mark.django_db
def test_hobby_category_multiple_filter(api_client, hobbycategory_hierarchy_root):
    """ Hobbies should be filterable using multiple category ids handled as OR logic """
    first_category = hobbycategory_hierarchy_root.get_children().first()
    last_category = hobbycategory_hierarchy_root.get_children().last()
    assert first_category != last_category, "test data is invalid, there should be multiple child categories"
    some_hobby = Hobby.objects.create(name="some hobby", category=first_category)
    another_hobby = Hobby.objects.create(name="another hobby", category=last_category)

    url = '{}?category={}&category={}'.format(reverse('hobby-list'), first_category.id, last_category.id)
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2
    returned_hobby_names = [hobby['name'] for hobby in response.data]
    assert some_hobby.name in returned_hobby_names
    assert another_hobby.name in returned_hobby_names


@pytest.mark.django_db
def test_hobby_category_hierarchical_filter(api_client, hobbycategory_hierarchy_root, hobby_category, hobby):
    """ Hobbies of child categories should be returned when filtering with parent category """
    first_category = hobbycategory_hierarchy_root.get_children().first()
    last_category = hobbycategory_hierarchy_root.get_children().last()
    hobby.category = hobby_category
    hobby.save()
    assert first_category != last_category, "test data is invalid, there should be multiple child categories"
    some_hobby = Hobby.objects.create(name="some hobby", category=first_category)
    another_hobby = Hobby.objects.create(name="another hobby", category=last_category)

    response = api_client.get(reverse('hobby-list'), {'category': hobbycategory_hierarchy_root.id})
    assert response.status_code == 200
    assert len(response.data) == 2
    returned_hobby_names = [hobby['name'] for hobby in response.data]
    assert some_hobby.name in returned_hobby_names
    assert another_hobby.name in returned_hobby_names
    assert hobby.name not in returned_hobby_names


@pytest.mark.django_db
def test_hobby_create(user_api_client, valid_hobby_data):
    """ Authenticated user should be able to create a new hobby """
    url = reverse('hobby-list')
    hobby_count = Hobby.objects.count()
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 201
    assert Hobby.objects.count() == hobby_count + 1
    latest_hobby = Hobby.objects.latest()
    for field in ['name', 'description']:
        assert getattr(latest_hobby, field) == valid_hobby_data.get(field)
    for id_field in ['category', 'location', 'organizer']:
        assert getattr(latest_hobby, f'{id_field}_id') == valid_hobby_data.get(id_field)


@pytest.mark.django_db
def test_hobby_unauthenticated_create(api_client, valid_hobby_data):
    """ Unauthenticated user should not be able to create a new hobby """
    url = reverse('hobby-list')
    hobby_count = Hobby.objects.count()
    response = api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 401
    assert Hobby.objects.count() == hobby_count


@pytest.mark.django_db
def test_hobby_create_created_by(user, user_api_client, valid_hobby_data):
    """ When creating a hobby, authenticated user should be saved in the hobby """
    url = reverse('hobby-list')
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 201
    latest_hobby = Hobby.objects.latest()
    assert latest_hobby.created_by == user
