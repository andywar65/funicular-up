from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from djgeojson.fields import PointField
from filer.fields.image import FilerImageField
from PIL import Image
from tree_queries.models import TreeNode


class Folder(TreeNode):
    name = models.CharField(
        _("Name"),
        max_length=50,
    )
    description = models.TextField(_("Description"), null=True, blank=True)
    date = models.DateField(_("Date"), null=True, blank=True)
    geom = PointField(_("Location"), null=True, blank=True)

    class Meta:
        verbose_name = _("Folder")
        verbose_name_plural = _("Folders")
        ordering = (
            "parent_id",
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


STATUS = [
    ("UP", _("Uploaded to server")),
    ("DW", _("Downloaded to local")),
    ("RQ", _("Requested at server")),
    ("ST", _("Restored from local")),
    ("KI", _("Kill on server")),
]


class Entry(models.Model):
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, verbose_name=_("Folder")
    )
    image = FilerImageField(
        verbose_name=_("Image"),
        related_name="entry_image",
        on_delete=models.SET_NULL,
        null=True,
    )
    caption = models.CharField(_("Caption"), max_length=200, null=True, blank=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS,
        default="UP",
        editable=False,
    )

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")

    def set_as_downloaded(self):
        self.status = "DW"
        with Image.open(self.image.path) as im:
            if self.image.width >= self.image.height:
                im.thumbnail((int(self.image.width / self.image.height * 128), 128))
            else:
                im.thumbnail((128, int(self.image.height / self.image.width * 128)))
            im.save(self.image.path)
        self.save()
