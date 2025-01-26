from django.urls import path

from .views import FolderDetailView, FolderListView

app_name = "funicular_up"
urlpatterns = [
    path("folder/", FolderListView.as_view(), name="folder_list"),
    path("folder/<pk>/", FolderDetailView.as_view(), name="folder_detail"),
]
