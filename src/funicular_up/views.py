from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Entry, Folder


class FolderCreateForm(ModelForm):
    class Meta:
        model = Folder
        fields = ("parent", "name")


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


class FolderCreateView(LoginRequiredMixin, CreateView):
    model = Folder
    template_name = "funicular_up/folder_create.html"
    form_class = FolderCreateForm

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_create.html"]
        return super().get_template_names()

    def get_success_url(self):
        return reverse("funicular_up:folder_list")


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = Folder
    template_name = "funicular_up/folder_detail.html"

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_detail.html"]
        return super().get_template_names()


@login_required
def folder_delete_view(request, pk):
    if "Hx-Request" not in request.headers:
        raise Http404("Request without HTMX headers")
    elif not request.headers["Hx-Request"] == "true":
        raise Http404("Request without HTMX headers")
    folder = get_object_or_404(Folder, id=pk)
    parent = folder.parent
    folder.delete()
    if parent:
        return HttpResponseRedirect(
            reverse("funicular_up:folder_detail", kwargs={"pk": parent.id})
        )
    else:
        return HttpResponseRedirect(reverse("funicular_up:folder_list"))


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


class EntryDownloaded(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Entry.objects.filter(status__in=["UP", "KI"])

    def get(self, request, *args, **kwargs):
        entry = self.get_object()
        entry.set_as_downloaded()
        data = {"text": f"Entry {entry.id} deleted on server"}
        return Response(data)


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()


class EntryUpdateAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)
    serializer_class = ImageUploadSerializer
    queryset = Entry.objects.filter(status="RQ")

    def put(self, request, *args, **kwargs):
        entry = self.get_object()
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            img = serializer.validated_data["image"]
            entry.image.file.save(img.name, img)
            entry.status = "ST"
            entry.save()
            r_data = {"text": f"Entry {entry.id} restored on server"}
            return Response(r_data)
        else:
            r_data = {"text": f"Entry {entry.id} not restored on server"}
            return Response(r_data)
