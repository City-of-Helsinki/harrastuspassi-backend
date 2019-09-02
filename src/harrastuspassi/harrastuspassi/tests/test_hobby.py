import pytest
from django.db import IntegrityError


@pytest.mark.django_db
def test_hobby_without_name(hobby):
    hobby.name = None
    with pytest.raises(IntegrityError):
        hobby.save()
