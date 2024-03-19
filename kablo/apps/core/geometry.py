from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import GeoFunc

# from django.db.models import Aggregate


# class MergeLines(Aggregate):
#    name = "joined_geometries"
#    template = "ST_SetSRID(ST_Expand(ST_Extent(%(expressions)s), 1), 2056)"
#    allow_distinct = False


class Intersects(GeoFunc):
    function = "ST_Intersects"
    geom_param_pos = (0, 1)
    output_field = models.BooleanField()


class SplitLine(GeoFunc):
    function = "ST_Split"
    geom_param_pos = (0, 1)
    output_field = models.MultiLineStringField()


class Dump(GeoFunc):
    function = "ST_Dump"
    geom_param_pos = [0]
