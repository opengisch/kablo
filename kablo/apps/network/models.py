from django.contrib.gis.db import models


class NetworkNode(models.Model):
    geom = models.PointField(srid=2056)


class NetworkSegment(models.Model):
    geom = models.LineStringField(srid=2056)
    network_node_start = models.ForeignKey(
        NetworkNode, related_name="network_node_start", on_delete=models.CASCADE
    )
    network_node_end = models.ForeignKey(
        NetworkNode, related_name="network_node_end", on_delete=models.CASCADE
    )


class Track(models.Model):
    networkSegments = models.ManyToManyField(NetworkSegment)


class Tube(models.Model):
    networkSegments = models.ManyToManyField(NetworkSegment)


class Station(models.Model):
    position = models.PointField(srid=2056)


class Cable(models.Model):
    tubes = models.ManyToManyField(Tube)
    station_start = models.ForeignKey(
        Station, related_name="station_start", on_delete=models.CASCADE
    )
    station_end = models.ForeignKey(
        Station, related_name="station_end", on_delete=models.CASCADE
    )
