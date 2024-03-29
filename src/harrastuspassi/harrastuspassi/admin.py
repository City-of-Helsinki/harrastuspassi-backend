
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
    fields = ('start_date', 'start_time', 'start_weekday', 'end_date', 'end_time',)
    extra = 0


class HobbyAdmin(GuardedModelAdmin):
    inlines = (HobbyEventInline,)
    raw_id_fields = ('location', 'next_event',)
    filter_horizontal = ('categories',)
    list_display = ('name', 'location', 'created_at', 'updated_at')
    list_filter = ('price_type',
                   'municipality__name',
                   'organizer__name',
                   'location__name')
    search_fields = ('name',
                     'location__name',
                     'municipality__name',
                     'description',
                     'organizer__name',
                     'categories__name')


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
