from django.urls import path
from django.views.generic import RedirectView

from .views import (
    EntryCaptionUpdateView,
    EntryDetailView,
    EntryDownloaded,
    EntryStatusDetailView,
    EntryUpdateAPIView,
    FolderCreateView,
    FolderDetailView,
    FolderInitialCreateView,
    FolderListView,
    FolderUploadView,
    SendStatus,
    entry_delete_view,
    folder_delete_view,
)

app_name = "funicular_up"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="funicular_up:folder_list")),
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/create/", FolderCreateView.as_view(), name="folder_create"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
    path(
        "folder/<pk>/create/",
        FolderInitialCreateView.as_view(),
        name="folder_create_initial",
    ),
    path(
        "folder/<pk>/upload/",
        FolderUploadView.as_view(),
        name="folder_upload",
    ),
    path("folder/<pk>/delete/", folder_delete_view, name="folder_delete"),
    path("entry/<pk>/", EntryDetailView.as_view(), name="entry_detail"),
    path("entry/<pk>/caption/", EntryCaptionUpdateView.as_view(), name="entry_caption"),
    path("entry/<pk>/status/", EntryStatusDetailView.as_view(), name="entry_status"),
    path("entry/<pk>/delete/", entry_delete_view, name="entry_delete"),
    # API views
    path("status/", SendStatus.as_view(), name="send_status"),
    path("entry/<pk>/download/", EntryDownloaded.as_view(), name="entry_download"),
    path("entry/<pk>/upload/", EntryUpdateAPIView.as_view(), name="entry_upload"),
]
