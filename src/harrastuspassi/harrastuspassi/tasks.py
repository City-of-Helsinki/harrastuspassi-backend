
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user, get_users_with_perms, assign_perm, remove_perm
from harrastuspassi.models import Hobby, Promotion, Location


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
    user_ids_to_assign_perm = set(user_ids_that_should_have_perm) - set(user_ids_that_have_perm)
    users_to_assign_perm = get_user_model().objects.filter(id__in=user_ids_to_assign_perm)

    user_ids_to_remove_perm = set(user_ids_that_have_perm) - set(user_ids_that_should_have_perm)
    users_to_remove_perm = get_user_model().objects.filter(id__in=user_ids_to_remove_perm)

    # Because django-guardian doesn't have bulk remove for identities
    for user in users_to_remove_perm:
        remove_perm('change_hobby', user, hobby)

    assign_perm('change_hobby', users_to_assign_perm, hobby)


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
        hobby_ids_to_assign_perm = set(hobby_ids_user_should_have_perm_for) - set(hobby_ids_user_has_perm_for)
        hobbies_to_assign_perm = Hobby.objects.filter(id__in=hobby_ids_to_assign_perm)

        hobby_ids_to_remove_perm = set(hobby_ids_user_has_perm_for) - set(hobby_ids_user_should_have_perm_for)
        hobbies_to_remove_perm = Hobby.objects.filter(id__in=hobby_ids_to_remove_perm)

        remove_perm('change_hobby', user, hobbies_to_remove_perm)
        assign_perm('change_hobby', user, hobbies_to_assign_perm)


def update_promotion_permissions(promotion_id):
    promotion = Promotion.objects.get(pk=promotion_id)

    def get_users_that_should_have_edit_permission(promotion):
        qs = get_user_model().objects.none()
        if promotion.municipality:
            qs |= promotion.municipality.moderators.all()
        if promotion.created_by:
            qs |= get_user_model().objects.filter(pk=promotion.created_by.pk)
        return qs

    users_that_have_perm = get_users_with_perms(promotion, only_with_perms_in=['change_promotion'])
    user_ids_that_have_perm = [u.pk for u in users_that_have_perm]

    users_that_should_have_perm = get_users_that_should_have_edit_permission(promotion)
    user_ids_that_should_have_perm = [u.pk for u in users_that_should_have_perm]
    user_ids_to_assign_perm = set(user_ids_that_should_have_perm) - set(user_ids_that_have_perm)
    users_to_assign_perm = get_user_model().objects.filter(id__in=user_ids_to_assign_perm)

    user_ids_to_remove_perm = set(user_ids_that_have_perm) - set(user_ids_that_should_have_perm)
    users_to_remove_perm = get_user_model().objects.filter(id__in=user_ids_to_remove_perm)

    # Because django-guardian doesn't have bulk remove for identities
    for user in users_to_remove_perm:
        remove_perm('change_promotion', user, promotion)

    assign_perm('change_promotion', users_to_assign_perm, promotion)


def update_user_promotion_permissions(user_ids):
    users = get_user_model().objects.filter(id__in=user_ids)

    def get_promotions_user_should_have_edit_permission_for(user):
        qs = Promotion.objects.filter(municipality__in=user.municipalities_where_moderator.all())
        qs |= Promotion.objects.filter(created_by=user)
        return qs

    for user in users:
        promotions_user_has_perm_for = get_objects_for_user(user, 'change_promotion', Promotion)
        promotion_ids_user_has_perm_for = [h.pk for h in promotions_user_has_perm_for]

        promotions_user_should_have_perm_for = get_promotions_user_should_have_edit_permission_for(user)
        promotion_ids_user_should_have_perm_for = [h.pk for h in promotions_user_should_have_perm_for]
        promotion_ids_to_assign_perm = set(promotion_ids_user_should_have_perm_for) - set(promotion_ids_user_has_perm_for)
        promotions_to_assign_perm = Promotion.objects.filter(id__in=promotion_ids_to_assign_perm)

        promotion_ids_to_remove_perm = set(promotion_ids_user_has_perm_for) - set(promotion_ids_user_should_have_perm_for)
        promotions_to_remove_perm = Promotion.objects.filter(id__in=promotion_ids_to_remove_perm)

        remove_perm('change_promotion', user, promotions_to_remove_perm)
        assign_perm('change_promotion', user, promotions_to_assign_perm)


def update_location_permissions(location_id):
    location = Location.objects.get(pk=location_id)

    def get_users_that_should_have_edit_permission(location):
        qs = get_user_model().objects.none()
        if location.municipality:
            qs |= location.municipality.moderators.all()
        if location.created_by:
            qs |= get_user_model().objects.filter(pk=location.created_by.pk)
        return qs

    users_that_have_perm = get_users_with_perms(location, only_with_perms_in=['change_location'])
    user_ids_that_have_perm = [u.pk for u in users_that_have_perm]

    users_that_should_have_perm = get_users_that_should_have_edit_permission(location)
    user_ids_that_should_have_perm = [u.pk for u in users_that_should_have_perm]
    user_ids_to_assign_perm = set(user_ids_that_should_have_perm) - set(user_ids_that_have_perm)
    users_to_assign_perm = get_user_model().objects.filter(id__in=user_ids_to_assign_perm)

    user_ids_to_remove_perm = set(user_ids_that_have_perm) - set(user_ids_that_should_have_perm)
    users_to_remove_perm = get_user_model().objects.filter(id__in=user_ids_to_remove_perm)

    # Because django-guardian doesn't have bulk remove for identities
    for user in users_to_remove_perm:
        remove_perm('change_location', user, location)

    assign_perm('change_location', users_to_assign_perm, location)


def update_user_location_permissions(user_ids):
    users = get_user_model().objects.filter(id__in=user_ids)

    def get_locations_user_should_have_edit_permission_for(user):
        qs = Location.objects.filter(municipality__in=user.municipalities_where_moderator.all())
        qs |= Location.objects.filter(created_by=user)
        return qs

    for user in users:
        locations_user_has_perm_for = get_objects_for_user(user, 'change_location', Location)
        location_ids_user_has_perm_for = [l.pk for l in locations_user_has_perm_for]

        locations_user_should_have_perm_for = get_locations_user_should_have_edit_permission_for(user)
        location_ids_user_should_have_perm_for = [h.pk for h in locations_user_should_have_perm_for]
        location_ids_to_assign_perm = set(location_ids_user_should_have_perm_for) - set(location_ids_user_has_perm_for)
        locations_to_assign_perm = Location.objects.filter(id__in=location_ids_to_assign_perm)

        location_ids_to_remove_perm = set(location_ids_user_has_perm_for) - set(location_ids_user_should_have_perm_for)
        locations_to_remove_perm = Location.objects.filter(id__in=location_ids_to_remove_perm)

        remove_perm('change_location', user, locations_to_remove_perm)
        assign_perm('change_location', user, locations_to_assign_perm)
