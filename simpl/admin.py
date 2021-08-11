from django.contrib import admin
from django.utils.html import format_html

from . import models


@admin.register(models.Run)
class RunAdmin(admin.ModelAdmin):
    date_hierarchy = "date_created"
    list_display = ["manage", "name", "date_created", "status_display"]
    list_filter = ["game", "status"]

    def has_change_permission(self, *args, **kwargs):
        return False

    def manage(self, obj):
        """
        Return the management URL for this Run.
        """
        return format_html(
            '<a href="{url}" class="viewlink">Manage</a>',
            url=obj.get_absolute_url(),
        )

    def status_display(self, obj):
        return obj.get_status_display()

    status_display.short_description = "Status"


# @admin.register(models.Player)
# class PlayerAdmin(admin.ModelAdmin):
#     readonly_fields = ["user", "lobby", "character", "completed"]


@admin.register(models.APIToken)
class APITokenAdmin(admin.ModelAdmin):
    readonly_fields = ["token", "last_used"]
    list_display = ["__str__", "last_used"]
    date_hierarchy = "last_used"

    def has_change_permission(self, *args, **kwargs):
        return False
