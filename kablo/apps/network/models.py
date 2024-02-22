from django.contrib.gis.db import models


class NetworkNode(models.Model):
    geom = models.PointField(srid=2056)


class TrackSection(models.Model):
    geom = models.LineStringField(srid=2056)
    network_node_start = models.ForeignKey(
        NetworkNode, related_name="network_node_start", on_delete=models.CASCADE
    )
    network_node_end = models.ForeignKey(
        NetworkNode, related_name="network_node_end", on_delete=models.CASCADE
    )


class Track(models.Model):
    networkSegments = models.ManyToManyField(
        TrackSection, through="TrackNetworkSegment"
    )

    geom = models.GeneratedField(
        expression=F("side") * F("side"),
        output_field=models.BigIntegerField(),
        db_persist=True,
    )

    def save(self, **kwargs):
        if not self.networkSegments:
            network_segment = TrackSection.objects.create()
            network_segment.geom = self.geom
            network_segment.save()

        super().save(**kwargs)

        self.networkSegments.add(network_segment)


class TrackTrackSection(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    network_node = models.ForeignKey(NetworkNode, on_delete=models.CASCADE)
    index = models.IntegerField()

    def save(self, **kwargs):
        if not self.index:
            self.index = len(self.track.networkSegments)

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
