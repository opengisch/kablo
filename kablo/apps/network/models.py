from django.contrib.gis.db import models


class NetworkNode(models.Model):
    pass


class TrackSection(models.Model):
    geom = models.LineStringField(srid=2056)
    network_node_start = models.ForeignKey(
        NetworkNode, related_name="network_node_start", on_delete=models.CASCADE
    )
    network_node_end = models.ForeignKey(
        NetworkNode, related_name="network_node_end", on_delete=models.CASCADE
    )


class Track(models.Model):
    networkSegments = models.ManyToManyField(TrackSection, through="TrackTrackSection")


class TrackTrackSection(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    network_node = models.ForeignKey(TrackSection, on_delete=models.CASCADE)
    index = models.IntegerField()

    def save(self, **kwargs):
        if not self.index:
            self.index = len(self.track.networkSegments)

        super().save(**kwargs)


class Tube(models.Model):
    networkSegments = models.ManyToManyField(TrackSection)


class Station(models.Model):
    geom = models.PointField(srid=2056)


class Node(models.Model):
    pass


class Reach(models.Model):
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
