
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user, get_users_with_perms, assign_perm, remove_perm
from harrastuspassi.models import Hobby


def update_hobby_permissions(hobby_id):
    hobby = Hobby.objects.get(pk=hobby_id)

    def get_users_that_should_have_edit_permission(hobby):
        qs = get_user_model().objects.none()
        if hobby.municipality:
            qs |= hobby.municipality.moderators.all()
        if hobby.created_by:
            qs |= get_user_model().objects.filter(pk=hobby.created_by.pk)
        return qs

    users_that_have_perm = get_users_with_perms(hobby, only_with_perms_in=['change_hobby'])
    user_ids_that_have_perm = [u.pk for u in users_that_have_perm]

    users_that_should_have_perm = get_users_that_should_have_edit_permission(hobby)
    user_ids_that_should_have_perm = [u.pk for u in users_that_should_have_perm]
    user_ids_that_should_have_perm = set(user_ids_that_should_have_perm) - set(user_ids_that_have_perm)
    users_that_should_have_perm = get_user_model().objects.filter(id__in=user_ids_that_should_have_perm)

    user_ids_that_should_not_have_perm = set(user_ids_that_have_perm) - set(user_ids_that_should_have_perm)
    users_that_should_not_have_perm = get_user_model().objects.filter(id__in=user_ids_that_should_not_have_perm)

    # Because django-guardian doesn't have bulk remove for identities
    for user in users_that_should_not_have_perm:
        remove_perm('change_hobby', user, hobby)

    assign_perm('change_hobby', users_that_should_have_perm, hobby)


def update_user_hobby_permissions(user_ids):
    users = get_user_model().objects.filter(id__in=user_ids)

    def get_hobbies_user_should_have_edit_permission_for(user):
        qs = Hobby.objects.filter(municipality__in=user.municipalities_where_moderator.all())
        qs |= Hobby.objects.filter(created_by=user)
        return qs

    for user in users:
        hobbies_user_has_perm_for = get_objects_for_user(user, 'change_hobby', Hobby)
        hobby_ids_user_has_perm_for = [h.pk for h in hobbies_user_has_perm_for]

        hobbies_user_should_have_perm_for = get_hobbies_user_should_have_edit_permission_for(user)
        hobby_ids_user_should_have_perm_for = [h.pk for h in hobbies_user_should_have_perm_for]
        hobby_ids_user_should_have_perm_for = set(hobby_ids_user_should_have_perm_for) - set(hobby_ids_user_has_perm_for)
        hobbies_user_should_have_perm_for = Hobby.objects.filter(id__in=hobby_ids_user_should_have_perm_for)

        hobby_ids_user_should_not_have_perm_for = set(hobby_ids_user_has_perm_for) - set(hobby_ids_user_should_have_perm_for)
        hobbies_user_should_not_have_perm_for = Hobby.objects.filter(id__in=hobby_ids_user_should_not_have_perm_for)

        remove_perm('change_hobby', user, hobbies_user_should_not_have_perm_for)
        assign_perm('change_hobby', user, hobbies_user_should_have_perm_for)
