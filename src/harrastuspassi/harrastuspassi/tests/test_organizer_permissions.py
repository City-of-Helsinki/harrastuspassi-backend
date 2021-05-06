import pytest
from guardian.shortcuts import get_perms


@pytest.mark.django_db
def test_anonymous_user_has_no_edit_perm(organizer, guardian_anonymous_user):
    assert 'change_organizer' not in get_perms(guardian_anonymous_user, organizer)


@pytest.mark.django_db
def test_user_has_no_edit_perm(organizer, user):
    assert 'change_organizer' not in get_perms(user, organizer)


@pytest.mark.django_db
def test_creator_gets_edit_perm(organizer, user):
    assert organizer.created_by_id != user.pk
    assert 'change_organizer' not in get_perms(user, organizer)
    organizer.created_by = user
    organizer.save()
    assert 'change_organizer' in get_perms(user, organizer)


@pytest.mark.django_db
def test_multiple_saves(organizer, user):
    # There was a bug that caused multiple saves to toggle the perm
    assert 'change_organizer' not in get_perms(user, organizer)
    organizer.created_by = user
    organizer.save()
    assert 'change_organizer' in get_perms(user, organizer)
    organizer.save()
    assert 'change_organizer' in get_perms(user, organizer)


@pytest.mark.django_db
def test_municipality_moderator_gets_edit_perm(location, user):
    assert 'change_location' not in get_perms(user, location)
    location.municipality.moderators.add(user)
    assert 'change_location' in get_perms(user, location)
    location.municipality.moderators.remove(user)
    assert 'change_location' not in get_perms(user, location)
