# Generated by Django 5.0.3 on 2024-05-14 12:59

import uuid

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TrackSplit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.LineStringField(srid=2056),
                ),
                ("force_save", models.BooleanField(default=False)),
            ],
        ),
    ]
