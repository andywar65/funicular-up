from django.urls import path
from django.views.generic import RedirectView

from .views import (
    EntryDetailView,
    EntryDownloaded,
    EntryStatusDetailView,
    EntryUpdateAPIView,
    FolderDetailView,
    FolderListView,
    SendStatus,
    folder_delete_view,
)

app_name = "funicular_up"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="funicular_up:folder_list")),
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
    path("folder/<pk>/delete/", folder_delete_view, name="folder_delete"),
    path("entry/<pk>/", EntryDetailView.as_view(), name="entry_detail"),
    path("entry/<pk>/status/", EntryStatusDetailView.as_view(), name="entry_status"),
    # API views
    path("status/", SendStatus.as_view(), name="send_status"),
    path("entry/<pk>/download/", EntryDownloaded.as_view(), name="entry_download"),
    path("entry/<pk>/upload/", EntryUpdateAPIView.as_view(), name="entry_upload"),
]
