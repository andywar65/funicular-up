from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Entry, Folder, show_folder_tree


class FolderCreateForm(ModelForm):
    class Meta:
        model = Folder
        fields = ("parent", "name")


class FolderListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = "funicular_up/folder_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tree"] = show_folder_tree(context["object_list"].with_tree_fields())
        return context

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_list.html"]
        return super().get_template_names()


class FolderCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "funicular_up.add_folder"
    model = Folder
    template_name = "funicular_up/folder_create.html"
    form_class = FolderCreateForm

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_create.html"]
        return super().get_template_names()

    def get_success_url(self):
        return reverse("funicular_up:folder_detail", kwargs={"pk": self.object.id})


class FolderInitialCreateView(FolderCreateView):

    def get_initial(self):
        initial = super().get_initial()
        initial["parent"] = get_object_or_404(Folder, id=self.kwargs["pk"])
        return initial


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = Folder
    template_name = "funicular_up/folder_detail.html"

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_detail.html"]
        return super().get_template_names()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class FileFieldForm(forms.Form):
    file_field = MultipleFileField()


class FolderUploadView(PermissionRequiredMixin, FormView):
    permission_required = "funicular_up.change_folder"
    template_name = "funicular_up/folder_upload.html"
    form_class = FileFieldForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = get_object_or_404(Folder, id=kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.object
        return context

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_upload.html"]
        return super().get_template_names()

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for f in files:
            print("Foo")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("funicular_up:folder_detail", kwargs={"pk": self.object.id})


@permission_required("funicular_up.delete_folder")
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


class EntryCaptionUpdateForm(ModelForm):
    class Meta:
        model = Entry
        fields = ("caption",)


class EntryCaptionUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "funicular_up.change_entry"
    model = Entry
    template_name = "funicular_up/htmx/entry_caption_update.html"
    form_class = EntryCaptionUpdateForm
    context_object_name = "entry"

    def get_prefix(self):
        return f"entry-{self.object.id}"

    def get_template_names(self):
        if "Hx-Request" not in self.request.headers:
            raise Http404
        return super().get_template_names()

    def get_success_url(self):
        return (
            reverse("funicular_up:folder_detail", kwargs={"pk": self.object.folder.id})
            + f"#entry-{self.object.id}"
        )


@permission_required("funicular_up.delete_entry")
def entry_delete_view(request, pk):
    if "Hx-Request" not in request.headers:
        raise Http404("Request without HTMX headers")
    elif not request.headers["Hx-Request"] == "true":
        raise Http404("Request without HTMX headers")
    entry = get_object_or_404(Entry, id=pk)
    folder = entry.folder
    entry.delete()
    return HttpResponseRedirect(
        reverse("funicular_up:folder_detail", kwargs={"pk": folder.id})
    )


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
            entry.image.file.delete()
            entry.image.file.save(img.name, img)
            entry.status = "ST"
            entry.save()
            r_data = {"text": f"Entry {entry.id} restored on server"}
            return Response(r_data)
        else:
            r_data = serializer.errors
            return Response(r_data)
