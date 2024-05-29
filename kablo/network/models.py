import uuid

from computedfields.models import ComputedFieldsModel, computed
from django.contrib.gis.db import models
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.geos import LineString as GeosLineString
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction
from django.db.models import Max, Value
from django.db.models.functions import Coalesce
from django_oapif.decorators import register_oapif_viewset
from shapely import (
    LineString,
    MultiLineString,
    Point,
    distance,
    force_2d,
    line_merge,
    offset_curve,
)

from kablo.core.functions import Intersects, SplitLine
from kablo.core.utils import geodjango2shapely, shapely2geodjango
from kablo.valuelist.models import CableTensionType, StatusType, TubeCableProtectionType


class NetworkNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    geom = models.PointField(srid=2056, dim=3)


@register_oapif_viewset(crs=2056)
class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    original_id = models.TextField(null=True, editable=True)
    geom = models.MultiLineStringField(srid=2056, dim=3)

    @transaction.atomic
    def save(self, **kwargs):
        # calling the super method causes the state flags to change, so save the original value in advance
        is_adding = self._state.adding
        super().save(**kwargs)
        if is_adding:
            order_index = 0
            sections = []

            for part_geom in self.geom:
                section = Section(
                    geom=part_geom,
                    track=self,
                    order_index=order_index,
                )
                order_index += 1
                sections.append(section)

            Section.objects.bulk_create(sections)

    @transaction.atomic
    def split(self, split_line: GeosLineString):
        has_split = False
        order_index = 0
        sections_qs = (
            Section.objects.filter(track=self)
            .annotate(
                splitted_geom=models.Case(
                    models.When(
                        models.Q(Intersects("geom", split_line)),
                        then=SplitLine("geom", split_line),
                    ),
                    output_field=models.GeometryCollectionField(),
                ),
            )
            .order_by("order_index")
        )

        for section in sections_qs:
            if section.splitted_geom:
                has_split = True
                for split_part_idx, split_part in enumerate(section.splitted_geom):
                    if split_part_idx == 0:
                        section.geom = split_part
                    else:
                        order_index += 1
                        section = section.clone()
                        section.geom = split_part

                    section.order_index = order_index
                    section.save()
            elif has_split:
                # update the ordering indexes on following sections
                section.order_index = order_index
                section.save()
            else:
                # no need to update index if no intersection occurred
                pass

            order_index += 1

        if has_split:
            self.geom = Section.objects.filter(track=self).aggregate(
                union=Union("geom")
            )["union"]
            self.save()


@register_oapif_viewset(crs=2056)
class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    geom = models.LineStringField(srid=2056, dim=3)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0, null=False, blank=False)

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

    class Meta:
        unique_together = ("track", "order_index")
        ordering = ["track_id", "order_index"]

    def clone(self):
        new_kwargs = dict()
        for field in self._meta.fields:
            if field.name != "id":
                new_kwargs[field.name] = getattr(self, field.name)
        return Section(**new_kwargs)


@register_oapif_viewset(crs=2056)
class Cable(ComputedFieldsModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fake_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    identifier = models.TextField(null=True, blank=True)
    original_id = models.TextField(null=True, editable=True)
    tension = models.ForeignKey(
        CableTensionType,
        null=True,
        on_delete=models.SET_NULL,
    )
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL,
    )

    @computed(models.LineStringField(srid=2056, null=True))
    def geom(self):
        # TODO: check geometry exists + is coherent
        # TODO: check order_index is continuous
        cable_spacing = 0.1
        planar_offset = 1.1

        agg = self.cabletube_set.order_by("order_index").aggregate(
            geom=Union("tube__geom"),
            display_offset=ArrayAgg("display_offset"),
            cable_count=ArrayAgg("cable_count"),
        )
        geom = agg["geom"]
        if geom:
            geom = geodjango2shapely(geom)
            if geom.geom_type == "MultiLineString":
                parts = []
                for part, display_offset, cable_count in zip(
                    geom.geoms, agg["display_offset"], agg["cable_count"]
                ):

                    offset_x = (
                        (display_offset - (cable_count - 1) / 2) * Value(cable_spacing),
                    )

                    coords = list(part.coords)
                    original_start_point = coords[0][0:1]
                    original_end_point = coords[-1][0:1]

                    first_vertex_distance = distance(
                        Point(coords[0]), Point(coords[-1])
                    )
                    if first_vertex_distance > 1:
                        coords[0] = part.interpolate(0.5).coords[0]
                    else:
                        coords.pop(0)

                    last_vertex_distance = distance(
                        Point(coords[-1]), Point(coords[-2])
                    )
                    if last_vertex_distance > 1:
                        coords[-1] = part.interpolate(-0.5).coords[0]
                    else:
                        coords.pop(-1)

                    part = offset_curve(
                        LineString(coords), distance=offset_x, join_style="bevel"
                    )
                    part = LineString(
                        [original_start_point] + list(part) + [original_end_point]
                    )
                    parts.append(part)
                geom = line_merge(MultiLineString(parts))
            else:
                geom = force_2d(geom)
            geom = shapely2geodjango(geom)
        return geom


@register_oapif_viewset(crs=2056)
class Tube(ComputedFieldsModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=True
    )
    fake_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    original_id = models.TextField(null=True, blank=True, editable=True)
    status = models.ForeignKey(
        StatusType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    diameter = models.IntegerField(
        default=None, null=True, blank=True, help_text="Diameter in mm"
    )
    cable_protection_type = models.ForeignKey(
        TubeCableProtectionType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @computed(
        models.LineStringField(srid=2056, dim=3, null=True, blank=True),
    )
    def geom(self):
        # TODO: this should not be editable, but switching prevent from seeing it in admin
        # TODO: this should not be nullable?

        # TODO: check geometry exists + is coherent
        # TODO: check order_index is continuous

        # TODO recalculate cables on change

        agg = self.tubesection_set.order_by("order_index").aggregate(
            geom=Union("section__geom"),
            order_index=ArrayAgg("order_index"),
            offset_x=ArrayAgg("offset_x"),
            offset_z=ArrayAgg("offset_z"),
        )
        geom = agg["geom"]
        if geom:
            geom = geodjango2shapely(geom)
            parts = []
            for part, offset_x, offset_z in zip(
                geom.geoms, agg["offset_x"], agg["offset_z"]
            ):
                coords = list(part.coords)
                original_start_point = (
                    coords[0][0],
                    coords[0][1],
                    coords[0][2] + offset_z / 1000,
                )
                original_end_point = (
                    coords[-1][0],
                    coords[-1][1],
                    coords[-1][2] + offset_z / 1000,
                )

                first_vertex_distance = distance(Point(coords[0]), Point(coords[-1]))
                if first_vertex_distance > 1:
                    coords[0] = part.interpolate(0.5).coords[0]
                else:
                    coords.pop(0)

                last_vertex_distance = distance(Point(coords[-1]), Point(coords[-2]))
                if last_vertex_distance > 1:
                    coords[-1] = part.interpolate(-0.5).coords[0]
                else:
                    coords.pop(-1)

                part = offset_curve(
                    LineString(coords), distance=offset_x / 1000, join_style="mitre"
                )
                new_coords = []
                for point_offset, point_z in zip(part.coords, coords):
                    new_coords.append(point_offset + (point_z[2] + offset_z / 1000,))
                part = LineString(
                    [original_start_point] + new_coords + [original_end_point]
                )
                parts.append(part)
            geom = line_merge(MultiLineString(parts))
            geom = shapely2geodjango(geom)
        return geom


@register_oapif_viewset(geom_field=None)
class TubeSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE, null=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)
    order_index = models.IntegerField(default=0, null=False, blank=False)
    interpolated = models.BooleanField(default=False, null=False, blank=False)
    offset_x = models.IntegerField(null=False, blank=False, default=0)
    offset_z = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        ordering = ["order_index"]


@register_oapif_viewset(geom_field=None)
class CableTube(ComputedFieldsModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0, null=False, blank=False)
    display_offset = models.IntegerField(default=0, null=False, blank=False)

    @computed(models.IntegerField(default=0, null=False, blank=False))
    def cable_count(self):
        return CableTube.objects.filter(tube=self.tube).count()

    class Meta:
        ordering = ["order_index"]

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            self.display_offset = (
                CableTube.objects.filter(tube=self.tube).aggregate(
                    do=Coalesce(Max("display_offset"), -1)
                )["do"]
                + 1
            )
        super().save(**kwargs)


@register_oapif_viewset(crs=2056)
class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    original_id = models.TextField(null=True, editable=True)
    label = models.CharField(max_length=64, blank=True, null=True)
    geom = models.PointField(srid=2056, dim=3)


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)


class Reach(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    node_1 = models.ForeignKey(
        Node, related_name="node_1", blank=True, null=True, on_delete=models.SET_NULL
    )
    node_2 = models.ForeignKey(
        Node, related_name="node_2", blank=True, null=True, on_delete=models.SET_NULL
    )


class VirtualNode(Node):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Switch(Reach):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Terminal(Node):
    pass
