from django.contrib.gis.db import models


class NetworkSegment(models.Model):
    geom = models.LineStringField(srid=2056)


class Trasse(models.Model):
    networkSegments = models.ManyToManyField(NetworkSegment)


class Tube(models.Model):
    networkSegments = models.ManyToManyField(NetworkSegment)


class Station(models.Model):
    position = models.PointField(srid=2056)


class Cable(models.Model):
    tubes = models.ManyToManyField(Tube)
