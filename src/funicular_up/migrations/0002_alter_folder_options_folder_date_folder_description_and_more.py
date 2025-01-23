# Generated by Django 5.1.5 on 2025-01-23 21:18

import djgeojson.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("funicular_up", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="folder",
            options={
                "ordering": ("parent_id", "name"),
                "verbose_name": "Folder",
                "verbose_name_plural": "Folders",
            },
        ),
        migrations.AddField(
            model_name="folder",
            name="date",
            field=models.DateField(blank=True, null=True, verbose_name="Date"),
        ),
        migrations.AddField(
            model_name="folder",
            name="description",
            field=models.TextField(
                blank=True, null=True, verbose_name="Description"
            ),  # noqa
        ),
        migrations.AddField(
            model_name="folder",
            name="geom",
            field=djgeojson.fields.PointField(
                blank=True, null=True, verbose_name="Location"
            ),
        ),
        migrations.AddConstraint(
            model_name="folder",
            constraint=models.UniqueConstraint(
                condition=models.Q(("parent", None)),
                fields=("name",),
                name="unique_root_folder_name",
                violation_error_message="Root folder name must be unique",
            ),
        ),
    ]
