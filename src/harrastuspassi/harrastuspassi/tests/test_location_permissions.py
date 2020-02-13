import pytest
from guardian.shortcuts import get_perms


@pytest.mark.django_db
def test_anonymous_user_has_no_edit_perm(location, guardian_anonymous_user):
    assert 'change_location' not in get_perms(guardian_anonymous_user, location)


@pytest.mark.django_db
def test_user_has_no_edit_perm(location, user):
    assert 'change_location' not in get_perms(user, location)


@pytest.mark.django_db
def test_creator_gets_edit_perm(location, user):
    assert location.created_by_id != user.pk
    assert 'change_location' not in get_perms(user, location)
    location.created_by = user
    location.save()
    assert 'change_location' in get_perms(user, location)


@pytest.mark.django_db
def test_multiple_saves(location, user):
    # There was a bug that caused multiple saves to toggle the perm
    assert 'change_location' not in get_perms(user, location)
    location.created_by = user
    location.save()
    assert 'change_location' in get_perms(user, location)
    location.save()
    assert 'change_location' in get_perms(user, location)


@pytest.mark.django_db
def test_municipality_moderator_gets_edit_perm(location, user):
    assert 'change_location' not in get_perms(user, location)
    location.municipality.moderators.add(user)
    assert 'change_location' in get_perms(user, location)
    location.municipality.moderators.remove(user)
    assert 'change_location' not in get_perms(user, location)
