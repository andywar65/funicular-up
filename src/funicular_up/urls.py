from django.urls import path

from .views import EntryDownloaded, FolderDetailView, FolderListView, SendStatus

app_name = "funicular_up"
urlpatterns = [
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
    # API views
    path("status/", SendStatus.as_view(), name="send_status"),
    path("entry/<pk>/downloaded/", EntryDownloaded.as_view(), name="entry_downloaded"),
]
