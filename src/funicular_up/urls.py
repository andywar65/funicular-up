from django.urls import path

from .views import FolderDetailView, FolderListView, send_status, test_view

app_name = "funicular_up"
urlpatterns = [
    path("status/", send_status, name="send_status"),
    path("test/", test_view, name="test"),
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
]
