from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import Entry, Folder


class EntryAdmin(admin.TabularInline):
    model = Entry
    sortable_field_name = "position"
    extra = 0


@admin.register(Folder)
class FolderAdmin(LeafletGeoAdmin):
    list_display = (
        "name",
        "parent",
    )
    inlines = [
        EntryAdmin,
    ]
