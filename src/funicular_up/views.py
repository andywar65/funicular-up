from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    RedirectView,
    UpdateView,
)
from filer.models import Image
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Entry, Folder, show_folder_tree


class FolderCreateForm(ModelForm):
    address = forms.CharField(
        label="Address", required=False, help_text="Enter address to geolocate"
    )

    class Meta:
        model = Folder
        fields = ("parent", "name", "description", "date")


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


class FolderDateListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = "funicular_up/folder_list_date.html"

    def get_queryset(self):
        qs = Folder.objects.exclude(date=None).order_by("-date")
        return qs

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_list_date.html"]
        return super().get_template_names()


class FolderMapListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = "funicular_up/folder_list_map.html"

    def get_queryset(self):
        qs = Folder.objects.exclude(geom=None)
        return qs

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_list_map.html"]
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

    def form_valid(self, form):
        if form.cleaned_data["address"]:
            geolocator = Nominatim(user_agent="andywar65_funicular_up")
            try:
                loc = geolocator.geocode(form.cleaned_data["address"])
                if loc.longitude and loc.latitude:
                    form.instance.geom = {
                        "type": "Point",
                        "coordinates": [loc.longitude, loc.latitude],
                    }
            except GeocoderTimedOut:
                pass
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("funicular_up:folder_detail", kwargs={"pk": self.object.id})


class FolderInitialCreateView(FolderCreateView):

    def get_initial(self):
        initial = super().get_initial()
        initial["parent"] = get_object_or_404(Folder, id=self.kwargs["pk"])
        return initial


class FolderUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "funicular_up.change_folder"
    model = Folder
    template_name = "funicular_up/folder_update.html"
    form_class = FolderCreateForm

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_update.html"]
        return super().get_template_names()

    def form_valid(self, form):
        if form.cleaned_data["address"]:
            geolocator = Nominatim(user_agent="andywar65_funicular_up")
            try:
                loc = geolocator.geocode(form.cleaned_data["address"])
                if loc.longitude and loc.latitude:
                    form.instance.geom = {
                        "type": "Point",
                        "coordinates": [loc.longitude, loc.latitude],
                    }
            except GeocoderTimedOut:
                pass
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("funicular_up:folder_detail", kwargs={"pk": self.object.id})


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = Folder
    template_name = "funicular_up/folder_detail.html"

    def get_template_names(self):
        if "Hx-Request" in self.request.headers:
            return ["funicular_up/htmx/folder_detail.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tree"] = show_folder_tree(self.object.descendants().with_tree_fields())
        return context


class FolderRequestAllDetailView(FolderDetailView):

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        for entry in obj.entry_set.filter(status="DW"):
            entry.status = "RQ"
            entry.save()
        return obj


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
        last = self.object.entry_set.last()
        if last and last.position:
            pos = last.position + 1
        else:
            pos = 1
        files = form.cleaned_data["file_field"]
        for f in files:
            image = Image.objects.create(file=f)
            Entry.objects.create(folder=self.object, image=image, position=pos)
            pos += 1
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


class EntryDetailRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        entry = get_object_or_404(Entry, id=kwargs["pk"])
        if entry.status == "DW" or entry.status == "RQ":
            return (
                reverse("funicular_up:folder_detail", kwargs={"pk": entry.folder.id})
                + f"#entry-{entry.id}"
            )
        return reverse("funicular_up:entry_detail_available", kwargs={"pk": entry.id})

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if (
            "Hx-Request" in self.request.headers
            and self.request.headers["Hx-Request"] == "true"
        ):
            response["HX-Request"] = True
        return response


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = "funicular_up/entry_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status == "ST":
            obj.status = "KI"
            obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["previous"] = self.object.get_previous()
        context["next"] = self.object.get_next()
        return context

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
            reverse("funicular_up:entry_sort", kwargs={"pk": self.object.folder.id})
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
    for follower in folder.entry_set.filter(position__gt=entry.position):
        follower.position -= 1
        follower.save()
    entry.delete()
    return HttpResponseRedirect(
        reverse("funicular_up:entry_sort", kwargs={"pk": folder.id})
    )


@permission_required("funicular_up.change_entry")
def entry_sort_view(request, pk):
    """Updates POSTed position of entries,
    redirects to funicular_up:folder_detail,
    renders in #fup-content"""

    if "Hx-Request" not in request.headers:
        raise Http404("Request without HTMX headers")
    elif not request.headers["Hx-Request"] == "true":
        raise Http404("Request without HTMX headers")
    folder = get_object_or_404(Folder, id=pk)
    if "entry_list" in request.POST:
        i = 1
        id_list = request.POST.getlist("entry_list")
        for id in id_list:
            item = get_object_or_404(Entry, id=id)
            if not item.position == i:
                item.position = i
                item.save()
            i += 1
    template_name = "funicular_up/htmx/folder_sortable.html"
    context = {"object": folder}
    return TemplateResponse(
        request,
        template_name,
        context,
        headers={"HX-Request": True},
    )


class ValidateForm(forms.Form):
    q = forms.CharField(max_length=100)


def search_results_view(request):
    success = False
    template_name = "funicular_up/search_results.html"
    if "Hx-Request" in request.headers:
        template_name = "funicular_up/htmx/search_results.html"
    form = ValidateForm(request.GET)
    if form.is_valid():
        q = SearchQuery(request.GET["q"])
        v = SearchVector("name", "description")
        # search in folders
        folders = Folder.objects.all().annotate(rank=SearchRank(v, q))
        folders = folders.filter(rank__gt=0.01)
        if folders:
            folders = folders.order_by("-rank")
            success = True
        v = SearchVector("caption")
        # search in images
        images = Entry.objects.all().annotate(rank=SearchRank(v, q))
        images = images.filter(rank__gt=0.01)
        if images:
            images = images.order_by("-rank")
            success = True

        return TemplateResponse(
            request,
            template_name,
            {
                "search": request.GET["q"],
                "folders": folders,
                "images": images,
                "success": success,
            },
        )
    else:
        return TemplateResponse(
            request,
            template_name,
            {
                "success": success,
            },
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
