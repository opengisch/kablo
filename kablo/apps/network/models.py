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
            if not self.track_sections:
                track_section = TrackSection.objects.create()
                track_section.geom = self.geom
                track_section.save()
                self.track_sections.add(track_section)
            super().save(**kwargs)


class TrackTrackSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    track_section = models.ForeignKey(TrackSection, on_delete=models.CASCADE)
    index = models.IntegerField()

    def save(self, **kwargs):
        if not self.index:
            self.index = len(self.track.track_section)

        super().save(**kwargs)


class Tube(models.Model):
    networkSegments = models.ManyToManyField(TrackSection)


class Station(models.Model):
    geom = models.PointField(srid=2056)


class Cable(models.Model):
    station_start = models.ForeignKey(
        Station, related_name="station_start", on_delete=models.CASCADE
    )
    station_end = models.ForeignKey(
        Station, related_name="station_end", on_delete=models.CASCADE
    )

    tubes = models.ManyToManyField(Tube)


class Node(models.Model):
    pass


class Switch(models.Model):
    pass


class Clamp(models.Model):
    pass
