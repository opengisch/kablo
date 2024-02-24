# Generated by Django 5.0.2 on 2024-02-24 08:53

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkNode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=2056)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=2056)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('geom', django.contrib.gis.db.models.fields.LineStringField(srid=2056)),
            ],
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='network.node')),
            ],
            bases=('network.node',),
        ),
        migrations.CreateModel(
            name='Reach',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='node_1', to='network.node')),
                ('node_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='node_2', to='network.node')),
            ],
        ),
        migrations.CreateModel(
            name='TrackSection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('geom', django.contrib.gis.db.models.fields.LineStringField(srid=2056)),
                ('network_node_end', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='network_node_end', to='network.networknode')),
                ('network_node_start', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='network_node_start', to='network.networknode')),
            ],
        ),
        migrations.CreateModel(
            name='TrackTrackSection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('index', models.IntegerField(default=1)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.track')),
                ('track_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.tracksection')),
            ],
        ),
        migrations.AddField(
            model_name='track',
            name='track_sections',
            field=models.ManyToManyField(through='network.TrackTrackSection', to='network.tracksection'),
        ),
        migrations.CreateModel(
            name='Tube',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('track_sections', models.ManyToManyField(to='network.tracksection')),
            ],
        ),
        migrations.CreateModel(
            name='Cable',
            fields=[
                ('reach_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='network.reach')),
                ('tubes', models.ManyToManyField(to='network.tube')),
            ],
            bases=('network.reach',),
        ),
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('reach_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='network.reach')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.station')),
            ],
            bases=('network.reach',),
        ),
        migrations.CreateModel(
            name='VirtualNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='network.node')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.station')),
            ],
            bases=('network.node',),
        ),
    ]
