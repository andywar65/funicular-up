from django.urls import path

from .views import FolderDetailView, FolderListView, SendStatus

app_name = "funicular_up"
urlpatterns = [
    path("status/", SendStatus.as_view(), name="send_status"),
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
]
