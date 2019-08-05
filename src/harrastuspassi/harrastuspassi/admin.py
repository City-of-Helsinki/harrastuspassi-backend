
# -*- coding: utf-8 -*-

from django.contrib import admin
from harrastuspassi.models import HobbyCategory, Hobby, Location, Organizer
from mptt.admin import DraggableMPTTAdmin


class SysAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and request.user.is_superuser


class HobbyCategoryAdmin(DraggableMPTTAdmin):
    pass


class HobbyAdmin(admin.ModelAdmin):
    pass


class LocationAdmin(admin.ModelAdmin):
    pass


class OrganizerAdmin(admin.ModelAdmin):
    pass


site = SysAdminSite()
admin.site.register(HobbyCategory, HobbyCategoryAdmin)
admin.site.register(Hobby, HobbyAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Organizer, OrganizerAdmin)
