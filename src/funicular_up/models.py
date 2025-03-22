import nh3
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djgeojson.fields import PointField
from filer.fields.image import FilerImageField
from PIL import Image
from tree_queries.models import TreeNode


def show_folder_tree(queryset):
    if not queryset.exists():
        return _("<p>No subfolders yet</p>")
    tree = "<ul>"
    first = True
    depth = queryset.first().tree_depth
    first_depth = depth
    for fld in queryset:
        if first:
            tree += f"<li>{fld.get_no_htmx_url()} ({fld.entry_set.count()})</li>"
            first = False
        else:
            if fld.tree_depth == depth:
                tree += f"<li>{fld.get_no_htmx_url()} ({fld.entry_set.count()})</li>"
            elif fld.tree_depth > depth:
                tree += (
                    f"<ul><li>{fld.get_no_htmx_url()} ({fld.entry_set.count()})</li>"
                )
                depth = fld.tree_depth
            else:
                for d in range(depth - fld.tree_depth):
                    tree += "</ul>"
                tree += f"<li>{fld.get_no_htmx_url()} ({fld.entry_set.count()})</li>"
                depth = fld.tree_depth
    for d in range(depth + 1 - first_depth):
        tree += "</ul>"
    return tree


class Folder(TreeNode):
    name = models.CharField(
        _("Name"),
        max_length=50,
    )
    description = models.TextField(_("Description"), null=True, blank=True)
    date = models.DateField(
        _("Date"), null=True, blank=True, help_text=_("YYYY-mm-dd format")
    )
    geom = PointField(_("Location"), null=True, blank=True)

    class Meta:
        verbose_name = _("Folder")
        verbose_name_plural = _("Folders")
        ordering = (
            "parent_id",
            "date",
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "parent",
                    "name",
                ],
                name="unique_folder_name",
            ),
            models.UniqueConstraint(
                fields=[
                    "name",
                ],
                condition=Q(parent=None),
                name="unique_root_folder_name",
                violation_error_message=_("Root folder name must be unique"),
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("funicular_up:folder_detail", kwargs={"pk": self.id})

    def get_htmx_url(self):
        url = f'<a href="#" hx-get="{self.get_absolute_url()}" '
        url += 'hx-target="#fup-content" hx-push-url="true">'
        url += f"{nh3.clean(self.name)}</a>"
        return url

    def get_no_htmx_url(self):
        url = f'<a href="{self.get_absolute_url()}">'
        url += f"{nh3.clean(self.name)}</a>"
        return url

    @property
    def popupContent(self):
        title_str = (
            f'<a href="{self.get_absolute_url()}"><strong>{self.name}</strong></a>'
        )
        if self.description:
            title_str += f"<p>{self.description}</p>"
        return {"content": title_str}


STATUS = [
    ("UP", _("Uploaded to server")),
    ("DW", _("Downloaded to local")),
    ("RQ", _("Requested on server")),
    ("ST", _("Restored from local")),
    ("KI", _("Kill on server")),
]


class Entry(models.Model):
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, verbose_name=_("Folder")
    )
    position = models.PositiveSmallIntegerField(_("Position"), null=True)
    image = FilerImageField(
        verbose_name=_("Image"),
        related_name="entry_image",
        on_delete=models.SET_NULL,
        null=True,
    )
    caption = models.CharField(_("Caption"), max_length=200, null=True, blank=True)
    status = models.CharField(
        _("Status"),
        max_length=2,
        choices=STATUS,
        default="UP",
        # editable=False,
    )

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")
        ordering = ["position", "id"]

    def set_as_downloaded(self):
        self.status = "DW"
        with Image.open(self.image.path) as im:
            if self.image.width >= self.image.height:
                im.thumbnail((int(self.image.width / self.image.height * 128), 128))
            else:
                im.thumbnail((128, int(self.image.height / self.image.width * 128)))
            im.save(self.image.path)
        self.save()

    def get_previous(self):
        try:
            prev = Entry.objects.get(
                folder=self.folder,
                position=(self.position - 1),
                status__in=["UP", "ST", "KI"],
            )
            return prev
        except Entry.DoesNotExist:
            return None

    def get_next(self):
        try:
            next = Entry.objects.get(
                folder=self.folder,
                position=(self.position + 1),
                status__in=["UP", "ST", "KI"],
            )
            return next
        except Entry.DoesNotExist:
            return None
