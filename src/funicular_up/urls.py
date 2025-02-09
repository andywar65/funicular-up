from django.urls import path

from .views import (
    EntryDetailView,
    EntryDownloaded,
    EntryStatusDetailView,
    EntryUpdateAPIView,
    FolderDetailView,
    FolderListView,
    SendStatus,
)

app_name = "funicular_up"
urlpatterns = [
    path("", FolderListView.as_view(), name="home"),
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
    path("entry/<pk>/", EntryDetailView.as_view(), name="entry_detail"),
    path("entry/<pk>/status/", EntryStatusDetailView.as_view(), name="entry_status"),
    # API views
    path("status/", SendStatus.as_view(), name="send_status"),
    path("entry/<pk>/download/", EntryDownloaded.as_view(), name="entry_download"),
    path("entry/<pk>/upload/", EntryUpdateAPIView.as_view(), name="entry_upload"),
]
