# Generated by Django 5.0.3 on 2024-05-16 12:13

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CableTensionType",
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
                ("original_id", models.TextField(null=True)),
                ("code", models.PositiveIntegerField()),
                ("name_fr", models.CharField(blank=True, max_length=64)),
                ("index", models.PositiveIntegerField(null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StatusType",
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
                ("original_id", models.TextField(null=True)),
                ("code", models.PositiveIntegerField()),
                ("name_fr", models.CharField(blank=True, max_length=64)),
                ("index", models.PositiveIntegerField(null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TubeCableProtectionType",
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
                ("original_id", models.TextField(null=True)),
                ("code", models.PositiveIntegerField()),
                ("name_fr", models.CharField(blank=True, max_length=64)),
                ("index", models.PositiveIntegerField(null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
