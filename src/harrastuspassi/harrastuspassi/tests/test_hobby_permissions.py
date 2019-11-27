import pytest
from guardian.shortcuts import get_perms


@pytest.mark.django_db
def test_anonymous_user_has_no_edit_perm(hobby, guardian_anonymous_user):
    assert 'change_hobby' not in get_perms(guardian_anonymous_user, hobby)


@pytest.mark.django_db
def test_user_has_no_edit_perm(hobby, user):
    assert 'change_hobby' not in get_perms(user, hobby)


@pytest.mark.django_db
def test_creator_gets_edit_perm(hobby, user):
    assert hobby.created_by_id != user.pk
    assert 'change_hobby' not in get_perms(user, hobby)
    hobby.created_by = user
    hobby.save()
    assert 'change_hobby' in get_perms(user, hobby)


@pytest.mark.django_db
def test_multiple_saves(hobby, user):
    # There was a bug that caused multiple saves to toggle the perm
    assert 'change_hobby' not in get_perms(user, hobby)
    hobby.created_by = user
    hobby.save()
    assert 'change_hobby' in get_perms(user, hobby)
    hobby.save()
    assert 'change_hobby' in get_perms(user, hobby)


@pytest.mark.django_db
def test_municipality_moderator_gets_edit_perm(hobby, user):
    assert 'change_hobby' not in get_perms(user, hobby)
    hobby.municipality.moderators.add(user)
    assert 'change_hobby' in get_perms(user, hobby)
    hobby.municipality.moderators.remove(user)
    assert 'change_hobby' not in get_perms(user, hobby)
