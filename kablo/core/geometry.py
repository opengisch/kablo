from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import GeoFunc
from django.contrib.postgres.fields import ArrayField


class Intersects(GeoFunc):
    function = "ST_Intersects"
    geom_param_pos = (0, 1)
    output_field = models.BooleanField()


class SplitLine(GeoFunc):
    function = "ST_Split"
    geom_param_pos = (0, 1)
    output_field = models.MultiLineStringField()


class AzimuthAlongLine(GeoFunc):
    function = "azimuth_along_line"
    geom_param_pos = (0,)
    output_field = ArrayField(models.IntegerField)
