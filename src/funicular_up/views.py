import json

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView

from .models import Entry, Folder


class FolderListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = "funicular_up/folder_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = context["object_list"].with_tree_fields()
        return context


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = Folder
    template_name = "funicular_up/folder_detail.html"


@permission_required("funicular_up.change_entry")
def send_status(request):
    entries = Entry.objects.filter(status="UP")
    data = {}
    for entry in entries:
        data[entry.id] = entry.image.url
    return JsonResponse(data)


def test_view(request):
    data = {"foo": "bar"}
    return JsonResponse(data)


def test_http_json_view(request):
    data = {"foo": "bar"}
    return HttpResponse(json.dumps(data), content_type="application/json")


def test_http_view(request):
    return HttpResponse("<p>application/json</p>")
