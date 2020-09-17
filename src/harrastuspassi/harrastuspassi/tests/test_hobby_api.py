import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse
from harrastuspassi.models import Hobby, Location
from rest_framework.exceptions import ErrorDetail


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
    some_hobby = Hobby.objects.create(name="some hobby")
    some_hobby.categories.add(first_category)
    another_hobby = Hobby.objects.create(name="another hobby")
    another_hobby.categories.add(last_category)

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
    some_hobby = Hobby.objects.create(name="some hobby")
    some_hobby.categories.add(first_category)
    another_hobby = Hobby.objects.create(name="another hobby")
    another_hobby.categories.add(last_category)

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
    hobby.categories.add(hobby_category)
    hobby.save()
    assert first_category != last_category, "test data is invalid, there should be multiple child categories"
    some_hobby = Hobby.objects.create(name="some hobby")
    some_hobby.categories.add(first_category)
    another_hobby = Hobby.objects.create(name="another hobby")
    another_hobby.categories.add(last_category)

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
    for id_field in ['location', 'organizer']:
        assert getattr(latest_hobby, f'{id_field}_id') == valid_hobby_data.get(id_field)
    assert set(latest_hobby.categories.all().values_list('pk', flat=True)) == set(valid_hobby_data['categories'])


@pytest.mark.django_db
def test_hobby_create_as_municipality_moderator(user_api_client, valid_hobby_data, user, municipality):
    url = reverse('hobby-list')
    municipality.moderators.add(user)
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    latest_hobby = Hobby.objects.latest()
    assert latest_hobby.municipality_id == municipality.pk


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


@pytest.mark.django_db
def test_hobby_update(user_api_client, valid_hobby_data):
    """ Authenticated user should be able to edit their hobbies """
    url = reverse('hobby-list')
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 201
    hobby_data = response.data.copy()
    hobby_data['name'] = 'A changed name'
    update_url = reverse('hobby-detail', kwargs={'pk': hobby_data['id']})
    response = user_api_client.put(update_url, data=hobby_data, format='json')
    assert response.status_code == 200
    hobby_obj = Hobby.objects.get(id=response.data['id'])
    assert hobby_obj.name == hobby_data['name']
    # test put without cover_image in hobby data
    # due to Base64ImageField causing unwanted behaviour
    # when used without required=False, allow_null=True
    hobby_data.pop('cover_image')
    response = user_api_client.put(update_url, data=hobby_data, format='json')
    assert response.status_code == 200


@pytest.mark.django_db
def test_hobby_update_another_user(user_api_client, user2_api_client, valid_hobby_data):
    """ Authenticated user should not be able to edit someone elses hobbies """
    url = reverse('hobby-list')
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 201
    hobby_data = response.data.copy()
    hobby_data['name'] = 'A changed name'
    update_url = reverse('hobby-detail', kwargs={'pk': hobby_data['id']})
    response = user2_api_client.put(update_url, data=hobby_data, format='json')
    assert response.status_code == 403
    hobby_obj = Hobby.objects.get(id=hobby_data['id'])
    assert hobby_obj.name == valid_hobby_data['name']


@pytest.mark.django_db
def test_hobby_update_unauthenticated_user(user_api_client, api_client, valid_hobby_data):
    """ Authenticated user should not be able to edit someone elses hobbies """
    url = reverse('hobby-list')
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 201
    hobby_data = response.data.copy()
    hobby_data['name'] = 'A changed name'
    update_url = reverse('hobby-detail', kwargs={'pk': hobby_data['id']})
    response = api_client.put(update_url, data=hobby_data, format='json')
    assert response.status_code == 401
    hobby_obj = Hobby.objects.get(id=hobby_data['id'])
    assert hobby_obj.name == valid_hobby_data['name']


@pytest.mark.django_db
def test_hobby_delete(user, user_api_client, hobby):
    """ Authenticated user should be able to delete their own hobby """
    url = reverse('hobby-detail', kwargs={'pk': hobby.pk})
    hobby.created_by = user
    hobby.save()
    response = user_api_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_hobby_delete_another_user(user2, user_api_client, hobby):
    """ Authenticated user should not be able to delete someone elses hobby """
    url = reverse('hobby-detail', kwargs={'pk': hobby.pk})
    hobby.created_by = user2
    hobby.save()
    response = user_api_client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_hobby_delete_unauthenticated_user(user, api_client, hobby):
    """ Unauthenticated user should not be able to delete someone elses hobby """
    url = reverse('hobby-detail', kwargs={'pk': hobby.pk})
    hobby.created_by = user
    hobby.save()
    response = api_client.delete(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_hobby_list_near_point(
    api_client,
    hobby_far,
    hobby_midway,
    hobby_near,
):
    """ Hobbies should be orderable by distance to a point """
    api_url = reverse('hobby-list')
    url = f'{api_url}?ordering=nearest&near_latitude=1.00000&near_longitude=1.00000'
    response = api_client.get(url)
    assert response.status_code == 200
    hobbies = response.json()
    assert hobby_near.pk == hobbies[0]['id']
    assert hobby_midway.pk == hobbies[1]['id']
    assert hobby_far.pk == hobbies[2]['id']
    # Reverse
    url = f'{api_url}?ordering=-nearest&near_latitude=1.00000&near_longitude=1.00000'
    response = api_client.get(url)
    assert response.status_code == 200
    hobbies = response.json()
    assert hobby_near.pk == hobbies[2]['id']
    assert hobby_midway.pk == hobbies[1]['id']
    assert hobby_far.pk == hobbies[0]['id']


@pytest.mark.django_db
def test_hobby_distance_filter(api_client):
    """
    Sorting Hobbies by distance should only return hobbies
    that are closer than value provided with max_distance query param
    """
    api_url = reverse('hobby-list')
    location_ylojarvi = Location.objects.create(name='Ylöjärvi', coordinates=Point(23.764732, 61.859539))
    location_sastamala = Location.objects.create(name='Sastamala', coordinates=Point(22.995811, 61.503266))
    location_orivesi = Location.objects.create(name='Orivesi', coordinates=Point(24.289451, 61.661839))
    Hobby.objects.create(name='Harrastus Ylöjärvellä', location=location_ylojarvi)
    Hobby.objects.create(name='Harrastus Sastamalassa', location=location_sastamala)
    Hobby.objects.create(name='Harrastus Orivedellä', location=location_orivesi)

    # Only location_orivesi should be within the distance provided in query params
    url = f'{api_url}?ordering=nearest&near_latitude=61.500986&near_longitude=23.762713&max_distance=35'
    response = api_client.get(url)
    assert len(response.data) == 1
    assert response.data[0]['location'] == location_orivesi.pk

    # Change max_distance to 50. All locations should be withing this distance
    url = f'{api_url}?ordering=nearest&near_latitude=61.500986&near_longitude=23.762713&max_distance=50'
    response = api_client.get(url)
    assert len(response.data) == 3


@pytest.mark.django_db
def test_hobby_price_validation(user_api_client, valid_hobby_data):
    # valid_hobby_data had valid price information as the name suggests
    url = reverse('hobby-list')
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 201

    # Change price to something else than 0, which shouldn't be allowed for free hobbies
    valid_hobby_data['price_amount'] = 808
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 400
    assert response.data['non_field_errors'][0] == ErrorDetail('Price amount has to be 0 if price type is free', code='invalid')

    # hobby_types other than free should not allow price of 0
    valid_hobby_data['price_type'] = Hobby.TYPE_ANNUAL
    valid_hobby_data['price_amount'] = 0
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 400
    assert response.data['non_field_errors'][0] == ErrorDetail('Price amount can not be 0 if price type is something else than free', code='invalid')


@pytest.mark.django_db
def test_hobby_default_price(user_api_client, valid_hobby_data):
    # by default, hobbies should be created with price_type free,
    # with the price_amount of 0
    url = reverse('hobby-list')
    if 'price_type' in valid_hobby_data:
        del valid_hobby_data['price_type']
    if 'price_amount' in valid_hobby_data:
        del valid_hobby_data['price_amount']
    assert 'price_type' not in valid_hobby_data and 'price_amount' not in valid_hobby_data

    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.data['price_type'] == Hobby.TYPE_FREE and response.data['price_amount'] == '0.00'


@pytest.mark.django_db
def test_hobby_positive_price(user_api_client, valid_hobby_data):
    # Negative hobby prices are not allowed
    url = reverse('hobby-list')
    valid_hobby_data['price_type'] = Hobby.TYPE_ANNUAL
    valid_hobby_data['price_amount'] = -1
    response = user_api_client.post(url, data=valid_hobby_data, format='json')
    assert response.status_code == 400
    assert response.data['non_field_errors'][0] == ErrorDetail('Price amount can not be negative', code='invalid')


@pytest.mark.django_db
def test_price_type_filter(user_api_client, location, organizer, municipality):
    url = reverse('hobby-list')
    free_type_hobby = Hobby.objects.create(
        name='Free type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_FREE
    )
    annual_type_hobby = Hobby.objects.create(
        name='Annual type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_ANNUAL
    )
    seasonal_type_hobby = Hobby.objects.create(
        name='Seasonal type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_SEASONAL
    )
    one_time_type_hobby = Hobby.objects.create(
        name='One time type hobby',
        location=location,
        organizer=organizer,
        municipality=municipality,
        price_type=Hobby.TYPE_ONE_TIME
    )
    response = user_api_client.get(url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 4

    # Filter for hobbies with price type of free
    url_with_free_filter = f'{url}?price_type={Hobby.TYPE_FREE}'
    response = user_api_client.get(url_with_free_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == free_type_hobby.name

    # Filter for hobbies with price type of annual
    url_with_annual_filter = f'{url}?price_type={Hobby.TYPE_ANNUAL}'
    response = user_api_client.get(url_with_annual_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == annual_type_hobby.name

    # Filter for hobbies with price type of seasonal
    url_with_seasonal_filter = f'{url}?price_type={Hobby.TYPE_SEASONAL}'
    response = user_api_client.get(url_with_seasonal_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == seasonal_type_hobby.name

    # Filter for hobbies with price type of one_time
    url_with_one_time_filter = f'{url}?price_type={Hobby.TYPE_ONE_TIME}'
    response = user_api_client.get(url_with_one_time_filter, format='json')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == one_time_type_hobby.name
