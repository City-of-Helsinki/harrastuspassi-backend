import pytest
from django.db import IntegrityError


@pytest.mark.django_db
def test_hobby_without_name(test_hobby):
  test_hobby.name = None
  with pytest.raises(IntegrityError) as e:
    test_hobby.save()
