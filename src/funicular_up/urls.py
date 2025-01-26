from django.urls import path

from .views import FolderListView

app_name = "funicular_up"
urlpatterns = [
    path("folder/", FolderListView.as_view(), name="folder_list"),
]
