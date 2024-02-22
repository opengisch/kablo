import uuid

from django.contrib.gis.db import models
from django.db import transaction

from kablo.apps.core.geometry import MergeLines


class NetworkNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.PointField(srid=2056)


class TrackSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.LineStringField(srid=2056)
    network_node_start = models.ForeignKey(
        NetworkNode,
        null=True,
        blank=True,
        related_name="network_node_start",
        on_delete=models.SET_NULL,
    )
    network_node_end = models.ForeignKey(
        NetworkNode,
        null=True,
        blank=True,
        related_name="network_node_end",
        on_delete=models.SET_NULL,
    )


class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.LineStringField(srid=2056)

    track_sections = models.ManyToManyField(TrackSection, through="TrackTrackSection")

    def compute_geom(self):
        return (
            self.track_sections.all()
            .order_by("index")
            .aggregate(geom=MergeLines("geom"))
            .values_list("geom")
        )

    def save(self, **kwargs):
        with transaction.atomic():
            if True:  # not self.track_sections:
                track_section = TrackSection.objects.create()
                track_section.geom = self.geom
                track_section.save()
                self.track_sections.add(track_section)

                track_section.save()
            super().save(**kwargs)


class TrackTrackSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    track_section = models.ForeignKey(TrackSection, on_delete=models.CASCADE)
    index = models.IntegerField(default=1)


class Tube(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track_sections = models.ManyToManyField(TrackSection)


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.PointField(srid=2056)


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Reach(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_1 = models.ForeignKey(
        Node, related_name="node_1", blank=True, null=True, on_delete=models.SET_NULL
    )
    node_2 = models.ForeignKey(
        Node, related_name="node_2", blank=True, null=True, on_delete=models.SET_NULL
    )


class Cable(Reach):
    tubes = models.ManyToManyField(Tube)


class VirtualNode(Node):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Switch(Reach):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Terminal(Node):
    pass
