import pytest
from django.urls import reverse
from harrastuspassi.models import Hobby


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

  response = api_client.get(f"{reverse('hobby-list')}?category={first_category.id}&category={last_category.id}")
  assert response.status_code == 200
  assert len(response.data) == 2
  returned_hobby_names = [hobby['name'] for hobby in response.data]
  assert some_hobby.name in returned_hobby_names
  assert another_hobby.name in returned_hobby_names
