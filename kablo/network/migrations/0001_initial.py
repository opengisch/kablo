# Generated by Django 5.0.3 on 2024-05-07 17:44

import uuid

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("valuelist", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NetworkNode",
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
                    django.contrib.gis.db.models.fields.PointField(dim=3, srid=2056),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Node",
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
            ],
        ),
        migrations.CreateModel(
            name="Reach",
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
                    "node_1",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="node_1",
                        to="network.node",
                    ),
                ),
                (
                    "node_2",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="node_2",
                        to="network.node",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Station",
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
                ("label", models.CharField(blank=True, max_length=64, null=True)),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.PointField(dim=3, srid=2056),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Track",
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
                (
                    "geom",
                    django.contrib.gis.db.models.fields.MultiLineStringField(
                        dim=3, srid=2056
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Cable",
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
                (
                    "geom",
                    django.contrib.gis.db.models.fields.LineStringField(
                        dim=3, null=True, srid=2056
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="valuelist.statustype",
                    ),
                ),
                (
                    "tension",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="valuelist.cabletensiontype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Terminal",
            fields=[
                (
                    "node_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="network.node",
                    ),
                ),
            ],
            bases=("network.node",),
        ),
        migrations.CreateModel(
            name="Section",
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
                    django.contrib.gis.db.models.fields.LineStringField(
                        dim=3, srid=2056
                    ),
                ),
                ("order_index", models.IntegerField(default=0)),
                (
                    "network_node_end",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="network_node_end",
                        to="network.networknode",
                    ),
                ),
                (
                    "network_node_start",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="network_node_start",
                        to="network.networknode",
                    ),
                ),
                (
                    "track",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="network.track"
                    ),
                ),
            ],
            options={
                "ordering": ["track_id", "order_index"],
                "unique_together": {("track", "order_index")},
            },
        ),
        migrations.CreateModel(
            name="Tube",
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
                (
                    "geom",
                    django.contrib.gis.db.models.fields.LineStringField(
                        dim=3, null=True, srid=2056
                    ),
                ),
                (
                    "cable_protection_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="valuelist.tubecableprotectiontype",
                    ),
                ),
                ("cables", models.ManyToManyField(to="network.cable")),
                (
                    "status",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="valuelist.statustype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CableTube",
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
                ("order_index", models.IntegerField(default=0)),
                (
                    "cable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="network.cable"
                    ),
                ),
                (
                    "tube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="network.tube"
                    ),
                ),
            ],
            options={
                "ordering": ["order_index"],
            },
        ),
        migrations.CreateModel(
            name="TubeSection",
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
                ("order_index", models.IntegerField(default=1)),
                ("reversed", models.BooleanField(default=False)),
                ("interpolated", models.BooleanField(default=False)),
                ("offset_x", models.IntegerField(default=0)),
                ("offset_z", models.IntegerField(default=0)),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="network.section",
                    ),
                ),
                (
                    "tube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="network.tube"
                    ),
                ),
            ],
            options={
                "ordering": ["order_index"],
            },
        ),
        migrations.AddField(
            model_name="tube",
            name="sections",
            field=models.ManyToManyField(
                through="network.TubeSection", to="network.section"
            ),
        ),
        migrations.CreateModel(
            name="VirtualNode",
            fields=[
                (
                    "node_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="network.node",
                    ),
                ),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="network.station",
                    ),
                ),
            ],
            bases=("network.node",),
        ),
        migrations.CreateModel(
            name="Switch",
            fields=[
                (
                    "reach_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="network.reach",
                    ),
                ),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="network.station",
                    ),
                ),
            ],
            bases=("network.reach",),
        ),
    ]
