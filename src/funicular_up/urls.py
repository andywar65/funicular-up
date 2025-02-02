from django.urls import path

from .views import (
    FolderDetailView,
    FolderListView,
    send_status,
    test_http_json_view,
    test_http_view,
    test_view,
)

app_name = "funicular_up"
urlpatterns = [
    path("status/", send_status, name="send_status"),
    path("test-json/", test_view, name="test_json"),
    path("test-http-json/", test_http_json_view, name="test_http_json"),
    path("test-http/", test_http_view, name="test_http"),
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
]
