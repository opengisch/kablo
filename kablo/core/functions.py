from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import GeoFunc
from django.contrib.postgres.fields import ArrayField


class AzimuthAlongLine(GeoFunc):
    function = "azimuth_along_line"
    geom_param_pos = (0,)
    output_field = ArrayField(models.IntegerField)


class EndPoint(GeoFunc):
    function = "ST_EndPoint"
    geom_param_pos = (0,)
    output_field = models.PointField()


class Force3D(GeoFunc):
    function = "ST_Force3D"
    geom_param_pos = (0,)
    output_field = models.GeometryField()


class Intersects(GeoFunc):
    function = "ST_Intersects"
    geom_param_pos = (0, 1)
    output_field = models.BooleanField()


class Length2d(GeoFunc):
    function = "ST_Length2D"
    geom_param_pos = (0,)
    output_field = models.DecimalField()


class Length3d(GeoFunc):
    function = "ST_Length3D"
    geom_param_pos = (0,)
    output_field = models.DecimalField()


class LineMerge(GeoFunc):
    function = "ST_LineMerge"
    geom_param_pos = (0,)
    output_field = models.LineStringField()


class LineSubstring(GeoFunc):
    function = "ST_LineSubstring"
    geom_param_pos = (0,)
    output_field = models.LineStringField()


class MakeLine(GeoFunc):
    function = "ST_MakeLine"
    geom_param_pos = (
        0,
        1,
    )
    output_field = models.LineStringField()


class Merge(GeoFunc):
    function = "ST_LineMerge"
    geom_param_pos = (0,)
    output_field = models.LineStringField()


class OffsetCurve(GeoFunc):
    function = "ST_OffsetCurve"
    geom_param_pos = (0,)
    output_field = models.LineStringField()


class ProjectZOnLine(GeoFunc):
    function = "project_z_on_line"
    geom_param_pos = (0, 1)
    output_field = models.LineStringField()


class StartPoint(GeoFunc):
    function = "ST_StartPoint"
    geom_param_pos = (0,)
    output_field = models.PointField()


class SplitLine(GeoFunc):
    function = "ST_Split"
    geom_param_pos = (0, 1)
    output_field = models.MultiLineStringField()
