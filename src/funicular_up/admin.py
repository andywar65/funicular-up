from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import Folder


@admin.register(Folder)
class FolderAdmin(LeafletGeoAdmin):
    list_display = (
        "name",
        "parent",
    )
