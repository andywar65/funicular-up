from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from tree_queries.models import TreeNode


class Folder(TreeNode):
    name = models.CharField(
        _("Name"),
        max_length=50,
    )

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
