
# -*- coding: utf-8 -*-

from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from mptt.admin import DraggableMPTTAdmin

from harrastuspassi.models import (
    Benefit,
    Hobby,
    HobbyCategory,
    HobbyEvent,
    Location,
    Municipality,
    Organizer,
    Promotion,
)


class SysAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and request.user.is_superuser


class HobbyCategoryAdmin(DraggableMPTTAdmin):
    pass


class HobbyEventInline(admin.TabularInline):
    model = HobbyEvent
    extra = 0


class HobbyAdmin(GuardedModelAdmin):
    inlines = (HobbyEventInline,)
    raw_id_fields = ('location',)
    filter_horizontal = ('categories',)


class LocationAdmin(admin.ModelAdmin):
    pass


class OrganizerAdmin(admin.ModelAdmin):
    pass


class MunicipalityAdmin(admin.ModelAdmin):
    filter_horizontal = ('moderators',)


class PromotionAdmin(admin.ModelAdmin):
    pass


class BenefitAdmin(admin.ModelAdmin):
    pass


site = SysAdminSite()
admin.site.register(Hobby, HobbyAdmin)
admin.site.register(HobbyCategory, HobbyCategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Benefit, BenefitAdmin)
