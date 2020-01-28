import pytest
from guardian.shortcuts import get_perms


@pytest.mark.django_db
def test_anonymous_user_has_no_edit_perm(promotion, guardian_anonymous_user):
    assert 'change_promotion' not in get_perms(guardian_anonymous_user, promotion)


@pytest.mark.django_db
def test_user_has_no_edit_perm(promotion, user):
    assert 'change_promotion' not in get_perms(user, promotion)


@pytest.mark.django_db
def test_creator_gets_edit_perm(promotion, user):
    assert promotion.created_by_id != user.pk
    assert 'change_promotion' not in get_perms(user, promotion)
    promotion.created_by = user
    promotion.save()
    assert 'change_promotion' in get_perms(user, promotion)


@pytest.mark.django_db
def test_multiple_saves(promotion, user):
    # There was a bug that caused multiple saves to toggle the perm
    assert 'change_promotion' not in get_perms(user, promotion)
    promotion.created_by = user
    promotion.save()
    assert 'change_promotion' in get_perms(user, promotion)
    promotion.save()
    assert 'change_promotion' in get_perms(user, promotion)


@pytest.mark.django_db
def test_municipality_moderator_gets_edit_perm(promotion, user):
    assert 'change_promotion' not in get_perms(user, promotion)
    promotion.municipality.moderators.add(user)
    assert 'change_promotion' in get_perms(user, promotion)
    promotion.municipality.moderators.remove(user)
    assert 'change_promotion' not in get_perms(user, promotion)
