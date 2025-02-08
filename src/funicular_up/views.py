from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

# from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

# from rest_framework.parsers import FileUploadParser
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Entry, Folder


class FolderListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = "funicular_up/folder_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = context["object_list"].with_tree_fields()
        return context

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_list.html"]
        return super().get_template_names()


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = Folder
    template_name = "funicular_up/folder_detail.html"

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_detail.html"]
        return super().get_template_names()


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = "funicular_up/entry_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status == "ST":
            obj.status = "KI"
            obj.save()
        return obj

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/entry_detail.html"]
        return super().get_template_names()


class EntryStatusDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = "funicular_up/htmx/entry_status.html"
    context_object_name = "entry"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status == "DW":
            obj.status = "RQ"
            obj.save()
        return obj

    def get_template_names(self):
        if "Hx-Request" not in self.request.headers:
            raise Http404
        return super().get_template_names()


class SendStatus(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        entries = Entry.objects.filter(status__in=["UP", "RQ", "KI"])
        data = {}
        for entry in entries:
            data[entry.id] = {
                "url": entry.image.url,
                "status": entry.status,
            }
        return Response(data)


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ["image", "status"]


class EntryDownloaded(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # entry = get_object_or_404(Entry, id=kwargs["pk"])
        entry = self.get_object()
        entry.set_as_downloaded()
        data = {"text": f"Entry {entry.id} deleted on server"}
        return Response(data)


class EntryUpdateAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EntrySerializer

    # def put(self, request, filename, format=None):
    # entry = get_object_or_404(Entry, id=request.kwargs["pk"])
    # entry.status = "ST"
    # entry.image = request.FILES['file']
    # entry.save()
    # data = {"text": f"Entry {entry.id} restored on server"}
    # return Response(data)
