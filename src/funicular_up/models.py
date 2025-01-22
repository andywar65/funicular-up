from django.db import IntegrityError, models, transaction
from django.utils.crypto import get_random_string
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
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "parent",
                    "name",
                ],
                name="unique_folder_name",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # check for folder unique name
        try:
            # avoid TransactionManagementError
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            self.name = f"{self.name}_{get_random_string(7)}"
            super().save(*args, **kwargs)
